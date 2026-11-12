"""Verify the public code/data distribution and freshly reproduced certificates."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent;R=ROOT/'research'
sha=lambda b:hashlib.sha256(b).hexdigest()
def stable(x):
    if isinstance(x,dict):return {k:stable(v) for k,v in x.items() if k!='elapsed_seconds'}
    if isinstance(x,list):return [stable(v) for v in x]
    return x

def differences(a,b,path=''):
    if type(a) is not type(b):return [(path,a,b)]
    if isinstance(a,dict):
        return [v for k in sorted(set(a)|set(b)) for v in ([(path+'/'+k,a.get(k),b.get(k))] if k not in a or k not in b else differences(a[k],b[k],path+'/'+k))]
    if isinstance(a,list):
        if len(a)!=len(b):return [(path+'/length',len(a),len(b))]
        return [v for i,(x,y) in enumerate(zip(a,b)) for v in differences(x,y,path+'/'+str(i))]
    return [] if a==b else [(path,a,b)]

def compare_assay(old,fresh,name):
    """Retain exact discrete outputs; compare numerical references at stated precision."""
    if name=='ASSAY_MODELS.txt':
        a=list(map(float,old.read_text().split()));b=list(map(float,fresh.read_text().split()))
        assert len(a)==len(b)
        error=max(abs(x-y) for x,y in zip(a,b));assert error<=2e-13,(name,error)
        return dict(file=name,maximum_absolute_difference=error,tolerance=2e-13)
    a=stable(json.loads(old.read_text()));b=stable(json.loads(fresh.read_text()));environment={}
    if name=='ASSAY_AUDIT.json':
        # Each run's file hashes remain exact integrity checks of its own bytes.
        for key,folder,prefix in [('output_sha256',R/'results',''),('source_sha256',R/'assay_frontier','')]:
            for n,h in b[key].items():assert sha((folder/(prefix+n)).read_bytes())==h,(name,n)
        for n,h in a['output_sha256'].items():assert sha((old.parent/('Data_S13_'+n.lower())).read_bytes())==h,(name,n)
        a.pop('output_sha256');b.pop('output_sha256')
        # Compiler identity is provenance, not a scientific result. Retain both
        # identities in the report; counts, source hashes and tolerances stay exact.
        environment={'reference_compiler':a.pop('compiler'),'observed_compiler':b.pop('compiler')}
        assert all(isinstance(v,str) and v.strip() for v in environment.values())
        # The new runner accepts native engines. All scientific sources other
        # than this orchestration file must retain the original hashes.
        old_sources=a.pop('source_sha256')
        new_sources=b.pop('source_sha256')
        assert {k:v for k,v in old_sources.items() if k!='run.py'}=={k:v for k,v in new_sources.items() if k!='run.py'}
        environment.update(reference_runner_sha256=old_sources['run.py'],observed_runner_sha256=new_sources['run.py'])
    delta=differences(a,b);error=0.
    for path,x,y in delta:
        # Counts, seeds, pass/fail flags, protocol and source hashes stay exact.
        assert type(x) is float and type(y) is float,(name,path,x,y)
        error=max(error,abs(x-y));assert abs(x-y)<=2e-10,(name,path,x,y)
    return dict(file=name,maximum_absolute_difference=error,tolerance=2e-10,**environment)

def main():
    manifest=json.loads((ROOT/'RELEASE_MANIFEST.json').read_text())
    version=manifest['version']
    assert version.count('.')==2 and all(x.isdigit() for x in version.split('.')) and len(manifest['files'])>70
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and not p.is_relative_to(R/'results')}
    assert actual==set(manifest['files'])|{'RELEASE_MANIFEST.json'},sorted(actual-set(manifest['files'])-{'RELEASE_MANIFEST.json'})
    for name,h in manifest['files'].items():
        assert sha((ROOT/name).read_bytes())==h,name
        assert not any(x in name.lower() for x in ['manuscript','supplementary_information','typeset','editorial','complete.zip','completo.zip']),name
        assert Path(name).suffix.lower() not in {'.pdf','.tex','.docx','.doc','.tar','.gz'},name
        if name.endswith('.zip'): assert manifest.get('reviewed_computational_archives',{}).get(name)==h,name
    meta=json.loads((ROOT/'.zenodo.json').read_text());assert meta['license']=='MIT' and meta['version']==version and meta['upload_type']=='software'
    citation=(ROOT/'CITATION.cff').read_text()
    assert 'MIT' in citation and ('version: '+version+'\n') in citation
    execution=json.loads((R/'results/EXECUTION.json').read_text())
    count={'compile_from_source':11,'verified_native':9}[execution['engine_mode']]
    assert execution['status']=='PASS_EXACT_MATHEMATICAL_RESULTS' and len(execution['commands'])==count and all(x['exit_code']==0 for x in execution['commands'])
    compared=[];numerical_comparisons=[]
    for old in sorted((ROOT/'expected/core').iterdir()):
        fresh=R/'results'/old.name;assert fresh.is_file(),old.name
        if old.suffix=='.json':assert stable(json.loads(old.read_text()))==stable(json.loads(fresh.read_text())),old.name
        else:assert old.read_bytes().replace(b'\r\n',b'\n')==fresh.read_bytes().replace(b'\r\n',b'\n'),old.name
        compared.append(old.name)
    for prefix,folder in [('Data_S10_','supplement-v09/data'),('Data_S11_','supplement-v010/data'),('Data_S12_','supplement-v011/data'),('Data_S13_','supplement-v012/data')]:
        for old in sorted((R/folder).glob(prefix+'*')):
            name=old.name.removeprefix(prefix).upper().replace('.JSON','.json').replace('.CSV','.csv').replace('.TXT','.txt');fresh=R/'results'/name
            assert fresh.is_file(),name
            if name in {'ASSAY_AUDIT.json','ASSAY_MOMENTS.json','ASSAY_MODELS.txt'}:
                numerical_comparisons.append(compare_assay(old,fresh,name))
            elif old.suffix=='.json':
                delta=differences(stable(json.loads(old.read_text())),stable(json.loads(fresh.read_text())))
                if delta:
                    (R/'results/REPRODUCTION_DIFFERENCES.json').write_text(json.dumps(dict(file=name,differences=delta),indent=2)+'\n')
                    print(json.dumps(dict(file=name,difference_count=len(delta),first_differences=delta[:20]),indent=2),flush=True)
                assert not delta,name
            else:assert old.read_bytes().replace(b'\r\n',b'\n')==fresh.read_bytes().replace(b'\r\n',b'\n'),name
            compared.append(name)
    audit=json.loads((R/'results/KINETIC_AUDIT.json').read_text());assert audit['status']=='PASS_CERTIFIED_CONTINUOUS_TIME_FD7_WITNESS'
    cert=json.loads((R/'results/DESIGN_CERTIFICATE.json').read_text());assert cert['status']=='PASS_CERTIFIED_DESIGN_FRONTIER'
    power=json.loads((R/'results/DESIGN_POWER.json').read_text());assert power['status']=='PASS_EXACT_DECLARED_POWER' and power['rows']==120
    tutorial=json.loads((R/'results/DESIGN_TUTORIAL.json').read_text());assert tutorial['fixed_horizon_design']['sufficient_blocks_certified']==200326
    assay=json.loads((R/'results/ASSAY_AUDIT.json').read_text());assert assay['status']=='PASS_FROZEN_TRAJECTORY_CAMPAIGN' and len(assay['power'])==72
    out=dict(numerical_reference_comparisons=numerical_comparisons,assay_settings=72,design_contrast=cert['absolute_contrast'],power_rows=power['rows'],status='PASS_PUBLIC_CODE_DATA_REPRODUCTION',version=version,manifest_files=len(manifest['files']),compared_results=len(compared),compared_names=compared,kinetic_counts=audit['counts'],publication_scope='Software and mathematical data; manuscripts excluded',license='MIT')
    (R/'results/PUBLIC_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
