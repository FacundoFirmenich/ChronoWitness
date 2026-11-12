"""Verify the public code/data distribution and freshly reproduced certificates."""
from pathlib import Path
import csv,hashlib,json,math
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
        # Orchestration and the portable capital representation are versioned
        # changes. The protocol, moment code, and all other inputs match.
        old_sources=a.pop('source_sha256')
        new_sources=b.pop('source_sha256')
        portable_files={'run.py','simulate.cpp'}
        assert old_sources.keys()==new_sources.keys()
        assert all(old_sources[k]==new_sources[k] for k in old_sources.keys()-portable_files)
        environment.update(reference_runner_sha256=old_sources['run.py'],observed_runner_sha256=new_sources['run.py'],
                           reference_simulator_sha256=old_sources['simulate.cpp'],observed_simulator_sha256=new_sources['simulate.cpp'])
    delta=differences(a,b);error=0.
    for path,x,y in delta:
        # Counts, seeds, pass/fail flags, protocol and source hashes stay exact.
        assert type(x) is float and type(y) is float,(name,path,x,y)
        error=max(error,abs(x-y));assert abs(x-y)<=2e-10,(name,path,x,y)
    return dict(file=name,maximum_absolute_difference=error,tolerance=2e-10,**environment)

def compare_supplement():
    reference=R/'supplement-v08/data'
    fresh=R/'results/supplement-v08'
    names={p.name for p in reference.iterdir() if p.name[:7] in {'Data_S1','Data_S2','Data_S3','Data_S4','Data_S5'}}
    sums=dict(line.split('  ',1)[::-1] for line in (fresh/'SHA256SUMS').read_text().splitlines())
    assert names==set(sums)
    for name in sorted(names):
        old=(reference/name).read_bytes()
        new=(fresh/name).read_bytes()
        assert sha(new)==sums[name],name
        if name=='Data_S5_supplement_checks.json':
            expected,observed=json.loads(old),json.loads(new)
            old_sources=expected.pop('source_sha256')
            new_sources=observed.pop('source_sha256')
            assert expected==observed,name
            assert old_sources.keys()==new_sources.keys()
            for path,digest in new_sources.items():
                assert sha((R/path).read_bytes())==digest,path
                if path!='supplement-v08/build_supplement.py':
                    assert old_sources[path]==digest,path
        else:
            assert old.replace(b'\r\n',b'\n')==new.replace(b'\r\n',b'\n'),name
    return sorted(names)

def compare_validation_csv(old,fresh):
    continuous={'mean','second_moment','raw_slow','raw_fast','endpoint_slow','endpoint_fast','max_pathwise_error'}
    with old.open(newline='',encoding='utf8') as f, fresh.open(newline='',encoding='utf8') as g:
        reference,observed=csv.DictReader(f),csv.DictReader(g)
        assert reference.fieldnames==observed.fieldnames
        assert continuous.issubset(reference.fieldnames)
        maxima={k:0. for k in sorted(continuous)}
        for index,(a,b) in enumerate(zip(reference,observed,strict=True),start=2):
            assert a.keys()==b.keys() and None not in a
            for k in a.keys()-continuous:
                assert a[k]==b[k],(fresh.name,index,k,a[k],b[k])
            for k in continuous:
                x,y=float(a[k]),float(b[k])
                error=abs(x-y)
                assert math.isfinite(x) and math.isfinite(y) and error<=2e-10,(fresh.name,index,k,x,y)
                maxima[k]=max(maxima[k],error)
    return dict(file=fresh.name,maximum_absolute_difference=max(maxima.values()),
                maximum_by_field=maxima,tolerance=2e-10)

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
    compared=compare_supplement();numerical_comparisons=[]
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
            elif name=='ASSAY_VALIDATION_RAW.csv':
                # The samples and row identities are fixed. ABI-dependent
                # floating-point summaries use the same bound as the audit.
                numerical_comparisons.append(compare_validation_csv(old,fresh))
            elif old.suffix=='.json':
                expected=stable(json.loads(old.read_text()))
                observed=stable(json.loads(fresh.read_text()))
                if name=='KINETIC_AUDIT.json':
                    archived_hashes=expected.pop('output_sha256')
                    observed_hashes=observed.pop('output_sha256')
                    assert archived_hashes.keys()==observed_hashes.keys()
                    for artifact,digest in archived_hashes.items():
                        assert sha((old.parent/('Data_S11_'+artifact.lower())).read_bytes())==digest,artifact
                        assert sha((fresh.parent/artifact).read_bytes())==observed_hashes[artifact],artifact
                    # These same files are also compared by parsed JSON or
                    # line-ending-independent CSV in this verification pass.
                delta=differences(expected,observed)
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
