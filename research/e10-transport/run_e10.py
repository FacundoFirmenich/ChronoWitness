from pathlib import Path
import os,sys,json,zipfile,hashlib,time,traceback,urllib.request,shutil,resource
os.environ['OPENBLAS_NUM_THREADS']='1'
R=Path('/content/chronowitness-e10-20261111');R.mkdir(exist_ok=True)
def save(n,x):(R/n).write_text(json.dumps(x,indent=2,allow_nan=False))
def sha(f):
 h=hashlib.sha256()
 with open(f,'rb') as a:
  while b:=a.read(1048576):h.update(b)
 return h.hexdigest()
def main():
 start=time.monotonic()
 with zipfile.ZipFile('/content/E10_INPUTS.zip') as z:z.extractall(R)
 sys.path.insert(0,str(R));import e9_core as core
 import numpy as np,pandas as pd
 P=json.loads((R/'E10_PROTOCOL.json').read_text());entries=json.loads((R/'E10_COHORT.json').read_text());choices=json.loads((R/'MODEL_SELECTION.json').read_text())
 assert sha(R/'MODEL_SELECTION.json')==P['model_selection_sha256']
 assert sha(R/'E9_NUMERICAL_PROTOCOL.json')==P['inherited_protocol_sha256']
 save('STATUS.json',{'stage':'SOURCE_DOWNLOAD','protocol_sha256':sha(R/'E10_PROTOCOL.json')})
 source=R/'SOURCE.zip'
 if not source.exists():
  assert shutil.disk_usage(R).free>2_000_000_000
  with urllib.request.urlopen('https://zenodo.org/api/records/7808385/files/Nalecz-Jawecki_et_al--Source_Data.zip/content',timeout=120) as a,source.open('xb') as b:shutil.copyfileobj(a,b,1048576)
 assert source.stat().st_size==723609060 and sha(source)==P['source_sha256']
 O=R/'evaluation';O.mkdir(exist_ok=True);audits=[];summary=[];decisions=[];support=[]
 with zipfile.ZipFile(source) as z:
  # Audit EVERY source file before evaluating any response score.
  for entry in entries:
   with z.open(entry['name']) as f:d=pd.read_csv(f)
   assert not d.duplicated(['track_id','time_in_minutes']).any()
   assert d.groupby('time_in_minutes').is_light_pulse.nunique(dropna=False).max()==1
   assert set(d.is_light_pulse.unique())<={0,1}
   assert np.equal(d.time_in_minutes,np.floor(d.time_in_minutes)).all()
   audits.append(dict(file=entry['name'],date=entry['date_from_upstream_configuration'],rows=len(d),tracks=int(d.track_id.nunique()),first=int(d.time_in_minutes.min()),last=int(d.time_in_minutes.max()),input_consensus=True))
  save('SCHEMA_AUDIT.json',audits);del d
  save('STATUS.json',{'stage':'SCHEMA_PASS_EVALUATING','files':len(audits)})
  for entry in entries:
   for h in [5,10,20]:
    for alignment in [0,1]:
     x,target,meta=core.datasets(z,entry,h,alignment)
     ident=dict(file=Path(entry['name']).name,date=entry['date_from_upstream_configuration'],clock=entry['clock_minutes'],horizon=h,alignment=alignment)
     stem=Path(entry['name']).stem+f'_h{h}_a{alignment}'
     err={'persistence':-target}
     for model in ['history_no_input','history_input']:
      p=next(v for v in choices if v['horizon']==h and v['alignment']==alignment and v['model']==model)
      m=tuple(np.array(p[k]) for k in ['mean','scale','beta']);n=len(m[0]);err[model]=core.predict(x[:,:n],m)-target
     meta['value_band']=np.searchsorted(p['training_cuts'],meta.y)
     meta['pulse_band']=np.where(meta.pulse_age<0,'no_previous_pulse',np.where(meta.pulse_age<5,'0_4',np.where(meta.pulse_age<15,'5_14','15_plus')))
     base=err['history_input'];un=base.copy();guard=base.copy();dd=[]
     for tid,ix in meta.groupby('track').groups.items():
      ix=np.asarray(ix);ee=ix[meta.loc[ix,'stage'].to_numpy()=='early'];vv=ix[meta.loc[ix,'stage'].to_numpy()=='validation']
      c=float(np.mean(base[ee])) if len(ee)>=5 else 0.;accepted=False;b=None;a=None
      if len(ee)>=5:
       un[ix]-=c
       if len(vv)>=3:
        b=core.metrics(base[vv]);a=core.metrics(base[vv]-c)
        accepted=a['rmse']<b['rmse'] and a['q95']<=1.01*b['q95']
        if accepted:guard[ix]-=c
      dd.append(dict(track=int(tid),early_n=len(ee),validation_n=len(vv),correction=c,accepted=bool(accepted),validation_before=b,validation_after=a))
     err.update(local_unguarded=un,local_guarded=guard);mask=meta.stage=='late';late=meta.loc[mask].copy()
     support.append({**ident,'stages':{str(k):int(v) for k,v in meta.stage.value_counts().items()},'late_tracks':int(late.track.nunique())})
     for model,v in err.items():late[model+'_error']=v[mask]
     late.to_csv(O/(stem+'_residuals.csv.gz'),index=False,compression='gzip')
     (O/(stem+'_decisions.json')).write_text(json.dumps(dd,allow_nan=False))
     if len(late):
      for model in err:summary.append({**ident,'model':model,**core.metrics(late[model+'_error'])})
     else:summary.append({**ident,'status':'NOT_ESTIMABLE','reason':'No eligible late windows under unchanged temporal rule'})
   save('SUMMARY.json',summary);save('SUPPORT.json',support)
   print('EVALUATED',Path(entry['name']).name,flush=True)
 save('COMPLETE.json',{'status':'COMPLETE_LOCKED_TRANSPORT','seconds':time.monotonic()-start,'peak_rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'source_sha256':sha(source),'protocol_sha256':sha(R/'E10_PROTOCOL.json'),'numpy':np.__version__,'pandas':pd.__version__,'contexts':len(support),'refitted':False})
 save('STATUS.json',{'stage':'COMPLETE'})
if __name__=='__main__':
 try:main()
 except BaseException:save('STATUS.json',{'stage':'FAILED','error':traceback.format_exc()});raise
