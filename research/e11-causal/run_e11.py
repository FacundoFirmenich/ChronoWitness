from pathlib import Path
import os,sys,json,time,hashlib,zipfile,traceback,datetime,resource
os.environ['OPENBLAS_NUM_THREADS']='1'
R=Path('/content/chronowitness-e11-20261111');sys.path.insert(0,str(R))
import numpy as np,pandas as pd
import e9_core as core
from policy import causal,reference_one,CANDIDATES

def save(n,v):(R/n).write_text(json.dumps(v,indent=2,allow_nan=False))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def paired(e,v):
 b=core.metrics(e);a=core.metrics(v)
 return dict(n=b['n'],rmse=a['rmse'],q95=a['q95'],mae=a['mae'],bias=a['bias'],base_rmse=b['rmse'],base_q95=b['q95'],rmse_ratio=a['rmse']/b['rmse'] if b['rmse'] else None,q95_ratio=a['q95']/b['q95'] if b['q95'] else None,delta_mse=float(np.mean(v*v-e*e)))
def make_context(z,entry,h,alignment,choices):
 x,target,meta=core.datasets(z,entry,h,alignment);err={'persistence':-target}
 for model in ['history_no_input','history_input']:
  p=next(v for v in choices if v['horizon']==h and v['alignment']==alignment and v['model']==model)
  m=tuple(np.array(p[k]) for k in ['mean','scale','beta']);n=len(m[0]);pred=core.predict(x[:,:n],m)
  alt=x[:,:n]@(m[2][1:]/m[1])+m[2][0]-np.dot(m[0]/m[1],m[2][1:])
  assert np.allclose(pred,alt,rtol=0,atol=1e-12)
  err[model]=pred-target
 meta['value_band']=np.searchsorted(p['training_cuts'],meta.y)
 meta['pulse_band']=np.where(meta.pulse_age<0,-1,np.where(meta.pulse_age<5,0,np.where(meta.pulse_age<15,1,2)))
 base=err['history_input'];fixed=base.copy();corr=np.zeros((len(meta),8));lev=np.full((len(meta),8),-1,np.int8);ns=np.zeros((len(meta),8),np.int16);mt=np.full((len(meta),8),-1,np.int64);reasons=np.zeros((len(meta),8),np.int8);audits=[]
 for gi,(tid,ix) in enumerate(meta.groupby('track').groups.items()):
  ix=np.asarray(ix);g=meta.loc[ix];st=g.stage.to_numpy();early=ix[st=='early'];val=ix[st=='validation']
  if len(early)>=5 and len(val)>=3:
   c=float(np.mean(base[early]));b=core.metrics(base[val]);a=core.metrics(base[val]-c)
   if a['rmse']<b['rmse'] and a['q95']<=1.01*b['q95']:fixed[ix]-=c
  tt=g.origin.to_numpy(np.int64);ee=base[ix];pp=g.pulse_band.to_numpy(np.int64);bb=g.value_band.to_numpy(np.int64);ll=st=='late'
  cc,llv,nn,mm,rr=causal(tt,ee,pp,bb,ll,h)
  assert np.all(mm[nn>=6]<np.broadcast_to(tt[:,None],mm.shape)[nn>=6])
  corr[ix]=cc;lev[ix]=llv;ns[ix]=nn;mt[ix]=mm;reasons[ix]=rr
  if gi==0:
   queries=np.flatnonzero(ll)
   queries=queries[np.linspace(0,len(queries)-1,min(10,len(queries)),dtype=int)] if len(queries) else queries
   for i in queries:
    for k,p in enumerate(CANDIDATES):
     ref=reference_one(tt,ee,pp,bb,int(i),h,p)
     assert abs(ref[0]-cc[i,k])<1e-12 and tuple(ref[1:])==(int(llv[i,k]),int(nn[i,k]),int(mm[i,k]),int(rr[i,k]))
    masked=ee.copy();masked[tt+h>=tt[i]]=np.nan;query=np.zeros(len(tt),dtype=bool);query[i]=True
    check=causal(tt,masked,pp,bb,query,h)[0][i]
    assert np.allclose(check,cc[i],rtol=0,atol=1e-12)
   audits.append(dict(track=int(tid),queries=len(queries),candidate_checks=8*len(queries),future_mask_checks=len(queries),status='PASS'))
 err['fixed_guard']=fixed
 mask=meta.stage.to_numpy()=='late';late=meta.loc[mask].copy()
 for name,values in err.items():late[name+'_error']=values[mask]
 return late,corr[mask],lev[mask],ns[mask],mt[mask],reasons[mask],audits

def main(mode):
 started=time.monotonic();assert (R/'PREFLIGHT_COMPLETE.json').exists()
 P=json.loads((R/'E11_PROTOCOL.json').read_text());assert sha(R/'policy.py')==P['policy_source_sha256'];assert sha(R/'MODEL_SELECTION.json')==P['model_selection_sha256'];assert sha(R/'E9_NUMERICAL_PROTOCOL.json')==P['inherited_protocol_sha256']
 cohorts=json.loads((R/'COHORTS.json').read_text());choices=json.loads((R/'MODEL_SELECTION.json').read_text());selected=None
 if mode=='reserve':
  selected=json.loads((R/'SELECTED_POLICY.json').read_text());assert selected['status']=='FROZEN_BEFORE_RESERVE';assert selected['protocol_sha256']==sha(R/'E11_PROTOCOL.json');kselected=next(i for i,p in enumerate(CANDIDATES) if p['id']==selected['candidate']['id'])
 entries=cohorts[mode];O=R/mode;O.mkdir(exist_ok=True);summary=[];local=[];audit=[];supports=[]
 save('STATUS.json',{'stage':mode.upper()+'_RUNNING'})
 with zipfile.ZipFile(R/'SOURCE.zip') as z:
  for entry in entries:
   for h in [5,10,20]:
    for alignment in [0,1]:
     late,cc,level,ns,mt,reason,checks=make_context(z,entry,h,alignment,choices)
     stem=Path(entry['name']).stem+f'_h{h}_a{alignment}';ident=dict(context=stem,file=Path(entry['name']).name,date=entry['date'],family=entry['family'],horizon=h,alignment=alignment)
     audit.append({**ident,'checks':checks,'matured_targets_strictly_before_origins':True,'prediction_linear_algebra_match':True})
     supports.append({**ident,'windows':len(late),'cells':int(late.track.nunique())})
     if late.empty:
      summary.append({**ident,'status':'NOT_ESTIMABLE'});continue
     base=late.history_input_error.to_numpy();models={'fixed_guard':late.fixed_guard_error.to_numpy()}
     if mode=='development':
      for k,p in enumerate(CANDIDATES):models[p['id']]=base-cc[:,k]
     else:
      models.update(history_input=base,history_no_input=late.history_no_input_error.to_numpy(),persistence=late.persistence_error.to_numpy(),causal_selected=base-cc[:,kselected])
      late['causal_error']=models['causal_selected'];late['causal_correction']=cc[:,kselected];late['policy_level']=level[:,kselected];late['policy_support']=ns[:,kselected];late['latest_feedback_target']=mt[:,kselected];late['policy_reason']=reason[:,kselected]
      late.to_csv(O/(stem+'_atomic.csv.gz'),index=False,compression='gzip')
     groups=list(late.groupby(['pulse_band','value_band'],observed=True).indices.items())
     for model,v in models.items():
      row={**ident,'model':model,**paired(base,v),'active_n':int(np.count_nonzero(abs(v-base)>1e-15))};harm=0;total=0
      for key,idx in groups:
       ix=np.asarray(idx);r=paired(base[ix],v[ix]);state='DESCRIPTIVE' if len(ix)>=20 else 'LOW_SUPPORT'
       local.append({**ident,'model':model,'pulse_band':int(key[0]),'value_band':int(key[1]),'status':state,**r})
       if state=='DESCRIPTIVE':total+=1;harm+=int(r['q95']>1.01*r['base_q95']+1e-12)
      row.update(supported_local_nodes=total,local_tail_harms_1pct=harm,local_harm_fraction=harm/total if total else None);summary.append(row)
   save(mode.upper()+'_SUMMARY.json',summary);save(mode.upper()+'_LOCAL.json',local);save(mode.upper()+'_CAUSAL_AUDIT.json',audit);save(mode.upper()+'_SUPPORT.json',supports)
   print('EVALUATED',mode,Path(entry['name']).name,flush=True)
 elapsed=time.monotonic()-started
 if mode=='development':
  d=pd.DataFrame(summary);rank=[]
  for p in CANDIDATES:
   c=d[d.model==p['id']];days=[]
   for date,g in c.groupby('date'):
    days.append(dict(date=date,activity=float(g.active_n.sum()/g.n.sum()),mean_rmse_ratio=float(g.rmse_ratio.mean()),mean_local_harm_fraction=float(g.local_harm_fraction.mean()),mean_log_rmse_ratio=float(np.log(g.rmse_ratio).mean())))
   eligible=all(v['activity']>=.01 and v['mean_rmse_ratio']<=1.05 for v in days)
   key=[max(v['mean_local_harm_fraction'] for v in days),float(np.mean([v['mean_local_harm_fraction'] for v in days])),float(np.mean([v['mean_log_rmse_ratio'] for v in days])),p['id']]
   rank.append(dict(candidate=p,eligible=eligible,rank_key=key,days=days))
  rank.sort(key=lambda x:x['rank_key']);save('DEVELOPMENT_SELECTION.json',rank);eligible=[x for x in rank if x['eligible']]
  if not eligible:save('SELECTED_POLICY.json',dict(status='NO_ELIGIBLE_CANDIDATE_RESERVE_UNSCORED'));save('STATUS.json',{'stage':'DEVELOPMENT_GATE_FAILED'});return
  win=eligible[0];save('SELECTED_POLICY.json',dict(status='FROZEN_BEFORE_RESERVE',frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate=win['candidate'],rank_key=win['rank_key'],development_days=win['days'],protocol_sha256=sha(R/'E11_PROTOCOL.json'),policy_source_sha256=sha(R/'policy.py'),selection_table_sha256=sha(R/'DEVELOPMENT_SELECTION.json'),development_seconds=elapsed))
  save('STATUS.json',{'stage':'DEVELOPMENT_COMPLETE_RESERVE_NOT_STARTED'});print('SELECTED',win['candidate'],flush=True)
 else:
  save('COMPLETE.json',dict(status='COMPLETE_84_RESERVE_CONTEXTS',seconds=elapsed,peak_rss_kb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,contexts=len(supports),acquisitions=14,selected_policy_sha256=sha(R/'SELECTED_POLICY.json'),protocol_sha256=sha(R/'E11_PROTOCOL.json')));save('STATUS.json',{'stage':'RESERVE_COMPLETE'})

if __name__=='__main__':
 try:main(sys.argv[1])
 except BaseException:save('STATUS.json',{'stage':'FAILED','error':traceback.format_exc()});raise
