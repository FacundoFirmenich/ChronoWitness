"""Frozen E9 empirical evaluation; no synthetic observations or test tuning."""
from pathlib import Path
import os,json,time,hashlib,zipfile,traceback,resource,shutil
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parent
P=json.loads((R/'E9_NUMERICAL_PROTOCOL.json').read_text())
O=R/'evaluation';O.mkdir(exist_ok=True)
def save(n,x):(O/n).write_text(json.dumps(x,indent=2,allow_nan=False))
def metrics(e):
 e=np.asarray(e);return dict(n=len(e),rmse=float(np.sqrt(np.mean(e*e))),mae=float(np.mean(abs(e))),bias=float(np.mean(e)),q95=float(np.quantile(abs(e),.95)))
def datasets(archive,entry,h,offset):
 with archive.open(entry['name']) as f:d=pd.read_csv(f)
 assert d.groupby('time_in_minutes').is_light_pulse.nunique().max()==1
 pulses=d.groupby('time_in_minutes').is_light_pulse.first()
 tmin=int(d.time_in_minutes.min());tmax=int(d.time_in_minutes.max())
 ep=int(tmin+.35*(tmax-tmin));vp=int(tmin+.65*(tmax-tmin))
 uv=np.full(tmax-tmin+1,np.nan);uv[pulses.index.to_numpy(dtype=int)-tmin]=pulses.to_numpy()
 last=np.maximum.accumulate(np.where(uv==1,np.arange(tmin,tmax+1),-1000000))
 windows=[];xx=[];targets=[];shift=np.r_[np.arange(-19,1),np.arange(offset,h+offset)]
 for tid,g in d.groupby('track_id',sort=True):
  g=g.sort_values('time_in_minutes');ts=g.time_in_minutes.to_numpy(dtype=int)
  y=(g.nuc_ERKKTR_intensity_mean/g.img_ERKKTR_intensity_mean).to_numpy();good=np.isfinite(y)&(g.img_ERKKTR_intensity_mean.to_numpy()>0)&(g.nuc_area.to_numpy()>0)
  v=np.arange(19,len(g)-h)
  if not len(v):continue
  bad=np.r_[0,np.cumsum(~good)]
  keep=((ts[v]-tmin)%5==0)&(ts[v+h]-ts[v-19]==19+h)&(bad[v+h+1]-bad[v-19]==0)
  v=v[keep];t=ts[v];ix=t[:,None]+shift-tmin
  if not len(v):continue
  valid=(ix>=0).all(axis=1)&(ix<len(uv)).all(axis=1);v=v[valid];t=t[valid];ix=ix[valid]
  inp=uv[ix];valid=np.isfinite(inp).all(axis=1);v=v[valid];t=t[valid];inp=inp[valid]
  if not len(v):continue
  past=y[v[:,None]+np.arange(-19,1)];xx.append(np.c_[past,inp]);targets.append(y[v+h]-y[v])
  age=t-last[t-tmin];age=np.where(last[t-tmin]<tmin,-1,age)
  stage=np.where(t+h<=ep,'early',np.where((t>=ep+20)&(t+h<=vp),'validation',np.where(t>=vp+20,'late','purged')))
  windows.append(pd.DataFrame(dict(track=np.full(len(v),int(tid)),origin=t,y=y[v],target=y[v+h],stage=stage,pulse_age=age,selected=g.is_preselected.to_numpy(dtype=bool)[v])))
 if not xx:raise RuntimeError('No eligible windows: '+entry['name'])
 return np.concatenate(xx),np.concatenate(targets),pd.concat(windows,ignore_index=True)
def fit(X,y,weights,lam):
 mu=np.average(X,axis=0,weights=weights);sd=np.sqrt(np.average((X-mu)**2,axis=0,weights=weights));sd[sd<1e-12]=1
 Z=np.c_[np.ones(len(X)),(X-mu)/sd];w=weights/weights.sum()
 penalty=np.eye(Z.shape[1])*lam;penalty[0,0]=0
 beta=np.linalg.solve((Z.T*w)@Z+penalty,Z.T@(w*y))
 return mu,sd,beta
def predict(X,m):
 mu,sd,b=m;return b[0]+((X-mu)/sd)@b[1:]
def custody():
 D=Path('/content/drive/MyDrive/ChronoWitness/E9/20261111/evaluation')
 if not D.parent.parent.parent.parent.is_dir() or not Path('/content/drive/MyDrive').is_dir():return False
 D.mkdir(parents=True,exist_ok=True);rec={}
 for f in O.iterdir():
  if not f.is_file():continue
  h=hashlib.sha256(f.read_bytes()).hexdigest();q=D/f.name
  if q.exists() and hashlib.sha256(q.read_bytes()).hexdigest()!=h:raise RuntimeError('Drive conflict '+str(q))
  if not q.exists():shutil.copyfile(f,q)
  assert hashlib.sha256(q.read_bytes()).hexdigest()==h;rec[f.name]=h
 (D/'READBACK.json').write_text(json.dumps(rec,indent=2));return True
def main():
 started=time.monotonic();entries=[x for x in json.loads((R/'E9_COHORT_MANIFEST.json').read_text()) if x['role']!='ANCILLARY_DISTINCT_PROTOCOL']
 assert len(entries)==30 and (R/'PREFLIGHT_COMPLETE.json').exists()
 summary=[];choices=[];nodes=[]
 with zipfile.ZipFile(R/'ERK_Source_Data.zip') as archive:
  for h in P['horizons_minutes']:
   for offset in P['alignments']:
    cache={e['name']:datasets(archive,e,h,offset) for e in entries}
    train=[e for e in entries if e['role']=='TRAIN'];cal=[e for e in entries if e['role']=='CALIBRATION'];test=[e for e in entries if e['role']=='TEST']
    X=np.concatenate([cache[e['name']][0] for e in train]);y=np.concatenate([cache[e['name']][1] for e in train]);w=np.concatenate([np.full(len(cache[e['name']][1]),1/len(cache[e['name']][1])) for e in train])
    cuts=np.quantile(np.concatenate([cache[e['name']][2].y.to_numpy() for e in train]),[1/3,2/3])
    models={}
    for model in ['history_no_input','history_input']:
     n=20 if model=='history_no_input' else X.shape[1];scores=[];fitted=[]
     for lam in P['ridge_penalties']:
      m=fit(X[:,:n],y,w,lam);fitted.append(m)
      scores.append(float(np.mean([np.mean((predict(cache[e['name']][0][:,:n],m)-cache[e['name']][1])**2) for e in cal])))
     k=int(np.argmin(scores));models[model]=(n,fitted[k]);mu,sd,beta=fitted[k]
     choices.append(dict(horizon=h,alignment=offset,model=model,penalty=P['ridge_penalties'][k],calibration_mse=scores,mean=mu.tolist(),scale=sd.tolist(),beta=beta.tolist(),training_cuts=cuts.tolist()))
    for e in test:
     x,target,meta=cache[e['name']];meta=meta.copy();meta['value_band']=np.searchsorted(cuts,meta.y);meta['pulse_band']=np.where(meta.pulse_age<0,'no_previous_pulse',np.where(meta.pulse_age<5,'0_4',np.where(meta.pulse_age<15,'5_14','15_plus')))
     errs={'persistence':-target}
     for model,(n,m) in models.items():errs[model]=predict(x[:,:n],m)-target
     base=errs['history_input'];un=base.copy();guard=base.copy();dec=[]
     for tid,ix in meta.groupby('track').groups.items():
      ix=np.asarray(ix);early=ix[meta.loc[ix,'stage'].to_numpy()=='early'];val=ix[meta.loc[ix,'stage'].to_numpy()=='validation']
      correction=float(np.mean(base[early])) if len(early)>=5 else 0.;accepted=False
      if len(early)>=5:
       un[ix]-=correction
       if len(val)>=3:
        before=metrics(base[val]);after=metrics(base[val]-correction)
        accepted=after['rmse']<before['rmse'] and after['q95']<=1.01*before['q95']
        if accepted:guard[ix]-=correction
      dec.append(dict(track=int(tid),early_n=len(early),validation_n=len(val),correction=correction,accepted=accepted))
     errs.update(local_unguarded=un,local_guarded=guard)
     mask=meta.stage=='late';late=meta.loc[mask].copy()
     ident=dict(file=Path(e['name']).name,date=e['date_from_upstream_configuration'],clock=e['clock_minutes'],horizon=h,alignment=offset)
     for key,v in errs.items():late[key+'_error']=v[mask]
     stem=Path(e['name']).stem+f'_h{h}_a{offset}'
     late.to_csv(O/(stem+'_residuals.csv.gz'),index=False,compression='gzip')
     save(stem+'_decisions.json',dec)
     if late.empty:
      summary.append({**ident,'status':'NOT_ESTIMABLE','reason':'No late windows after temporal purge'});continue
     for key in errs:summary.append({**ident,'model':key,**metrics(late[key+'_error'])})
     # Parent, cell, each marginal and intersected local nodes preserve source identities.
     for dims in [['track'],['pulse_band'],['value_band'],['pulse_band','value_band']]:
      for values,g in late.groupby(dims,observed=True):
       for key in ['history_input','local_unguarded','local_guarded']:
        nodes.append({**ident,'dimensions':dims,'values':str(values),'model':key,'status':'DESCRIPTIVE' if len(g)>=20 else 'LOW_SUPPORT',**metrics(g[key+'_error'])})
     print('EVALUATED',stem,len(late),flush=True)
    save('MODEL_SELECTION.json',choices);save('SUMMARY.json',summary);save('LOCAL_NODES.json',nodes)
    del cache,X,y,w
 save('COMPLETE.json',{'status':'COMPLETE_PRIMARY_E9','seconds':time.monotonic()-started,'peak_rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'test_days':2,'numerical_protocol_sha256':hashlib.sha256((R/'E9_NUMERICAL_PROTOCOL.json').read_bytes()).hexdigest(),'direct_fd_validation':False})
 ok=custody();(R/'E9_EVALUATION_STATUS.json').write_text(json.dumps({'status':'COMPLETE','drive_verified':ok}))
if __name__=='__main__':
 try:main()
 except BaseException:
  (R/'E9_EVALUATION_STATUS.json').write_text(json.dumps({'status':'FAILED','error':traceback.format_exc()}));raise
