from pathlib import Path
import os,sys,json,zipfile,hashlib,time,subprocess,urllib.request,shutil,traceback
R=Path('/content/chronowitness-e11-20261111');R.mkdir(exist_ok=True)
def save(n,v):(R/n).write_text(json.dumps(v,indent=2))
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
try:
 start=time.monotonic()
 with zipfile.ZipFile('/content/E11_INPUTS.zip') as z:z.extractall(R)
 P=json.loads((R/'E11_PROTOCOL.json').read_text());save('STATUS.json',{'stage':'SOURCE_AND_ENVIRONMENT','protocol_sha256':digest(R/'E11_PROTOCOL.json')})
 subprocess.run([sys.executable,'-m','pip','install','--quiet','numpy==2.2.6','pandas==2.2.3','numba==0.61.2'],check=True)
 assert shutil.disk_usage(R).free>2_000_000_000
 source=R/'SOURCE.zip'
 with urllib.request.urlopen('https://zenodo.org/api/records/7808385/files/Nalecz-Jawecki_et_al--Source_Data.zip/content',timeout=120) as a,source.open('xb') as b:shutil.copyfileobj(a,b,1048576)
 assert source.stat().st_size==723609060 and digest(source)==P['source_sha256']
 import pandas as pd,numpy as np
 cohorts=json.loads((R/'COHORTS.json').read_text());audit=[]
 with zipfile.ZipFile(source) as z:
  for entry in cohorts['development']+cohorts['reserve']:
   with z.open(entry['name']) as f:d=pd.read_csv(f)
   assert not d.duplicated(['track_id','time_in_minutes']).any()
   assert d.groupby('time_in_minutes').is_light_pulse.nunique(dropna=False).max()==1
   assert set(d.is_light_pulse.unique())<={0,1}
   assert np.equal(d.time_in_minutes,np.floor(d.time_in_minutes)).all()
   audit.append(dict(file=entry['name'],cohort=entry['cohort'],date=entry['date'],rows=len(d),tracks=int(d.track_id.nunique()),first=int(d.time_in_minutes.min()),last=int(d.time_in_minutes.max()),input_consensus=True))
 save('SCHEMA_AUDIT.json',audit);save('PREFLIGHT_COMPLETE.json',dict(status='PASS_62_SCHEMAS',seconds=time.monotonic()-start,source_sha256=digest(source),protocol_sha256=digest(R/'E11_PROTOCOL.json')));save('STATUS.json',{'stage':'PREFLIGHT_COMPLETE'})
 print('PREFLIGHT_PASS',len(audit),flush=True)
except BaseException:save('STATUS.json',{'stage':'FAILED','error':traceback.format_exc()});raise
