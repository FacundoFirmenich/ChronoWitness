from pathlib import Path
import json,time,zipfile,hashlib,traceback
import numpy as np,pandas as pd
R=Path('/content/chronowitness-e9-20261111');O=R/'evaluation'
try:
 for i in range(180):
  f=R/'E9_EVALUATION_STATUS.json'
  if f.exists():
   s=json.loads(f.read_text())
   if s['status']=='FAILED':raise RuntimeError(s)
   if s['status']=='COMPLETE':break
  time.sleep(10)
 else:raise RuntimeError('Evaluation did not complete within verifier wait limit')
 rows=json.loads((O/'SUMMARY.json').read_text());verified=[]
 for f in sorted(O.glob('*_residuals.csv.gz')):
  df=pd.read_csv(f);stem=f.name.removesuffix('_residuals.csv.gz');dec=json.loads((O/(stem+'_decisions.json')).read_text());lookup={x['track']:x for x in dec}
  assert df.stage.eq('late').all();assert not df.duplicated(['track','origin']).any()
  assert np.allclose(df.persistence_error,df.y-df.target,rtol=0,atol=1e-12)
  corr=df.track.map(lambda t:lookup[t]['correction']);accept=df.track.map(lambda t:lookup[t]['accepted'])
  assert np.allclose(df.local_unguarded_error,df.history_input_error-corr,rtol=0,atol=1e-12)
  assert np.allclose(df.local_guarded_error,df.history_input_error-corr*accept,rtol=0,atol=1e-12)
  for model in ['persistence','history_no_input','history_input','local_unguarded','local_guarded']:
   h=int(stem.split('_h')[-1].split('_')[0]);a=int(stem.split('_a')[-1]);name=stem.split('_h')[0]+'.csv';row=next(r for r in rows if r.get('model')==model and r['file']==name and r['horizon']==h and r['alignment']==a)
   e=df[model+'_error'].to_numpy();assert row['n']==len(e)
   assert np.isclose(np.sqrt(np.mean(e**2)),row['rmse'],rtol=0,atol=1e-12)
   assert np.isclose(np.quantile(abs(e),.95),row['q95'],rtol=0,atol=1e-12)
  verified.append({'file':f.name,'rows':len(df),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 s=pd.DataFrame(rows);ix=['file','date','clock','horizon','alignment'];q=s.pivot(index=ix,columns='model',values='rmse');t=s.pivot(index=ix,columns='model',values='q95')
 stats={'contexts':len(q),'input_better_than_no_input':int((q.history_input<q.history_no_input).sum()),'guard_better_than_base':int((q.local_guarded<q.history_input-1e-12).sum()),'guard_rmse_harm_over_1pct':int((q.local_guarded>1.01*q.history_input).sum()),'unguarded_rmse_harm_over_1pct':int((q.local_unguarded>1.01*q.history_input).sum()),'guard_q95_harm_over_1pct':int((t.local_guarded>1.01*t.history_input).sum()),'unguarded_q95_harm_over_1pct':int((t.local_unguarded>1.01*t.history_input).sum())}
 nodes=pd.DataFrame(json.loads((O/'LOCAL_NODES.json').read_text()));nodes['dims']=nodes.dimensions.map(str)
 leaves=nodes[nodes.dims=="['pulse_band', 'value_band']"]
 qq=leaves.pivot(index=ix+['values'],columns='model',values='q95');nn=leaves.pivot(index=ix+['values'],columns='model',values='n');qq=qq[nn.history_input>=20]
 stats['supported_intersection_nodes']=len(qq);stats['intersection_guard_tail_harm_over_1pct']=int((qq.local_guarded>1.01*qq.history_input).sum());stats['intersection_unguarded_tail_harm_over_1pct']=int((qq.local_unguarded>1.01*qq.history_input).sum())
 stats['worst_guarded_local_q95_ratio']=float((qq.local_guarded/qq.history_input).max())
 out={'status':'PASS_INDEPENDENT_RESIDUAL_RECONSTRUCTION','files':verified,'summary':stats,'scope':'Checks atomic residual algebra, decisions and file metrics; does not independently refit models or establish biological causality.'}
 (R/'E9_VERIFICATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(stats),flush=True)
 with zipfile.ZipFile(R/'E9_RESULTS_AND_SOURCES.zip','x',zipfile.ZIP_DEFLATED) as z:
  for f in R.glob('*.json'):
   if f.name not in ['SHA256.json']:z.write(f,f.name)
  for f in R.glob('*.py'):z.write(f,'source/'+f.name)
  for f in O.iterdir():
   if f.is_file():z.write(f,'evaluation/'+f.name)
 (R/'PACKAGE_RECEIPT.json').write_text(json.dumps({'bytes':(R/'E9_RESULTS_AND_SOURCES.zip').stat().st_size,'sha256':hashlib.sha256((R/'E9_RESULTS_AND_SOURCES.zip').read_bytes()).hexdigest()}))
except BaseException:
 (R/'VERIFIER_FAILURE.json').write_text(json.dumps({'error':traceback.format_exc()}));raise
