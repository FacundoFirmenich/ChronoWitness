"""Verify the public code/data distribution and freshly reproduced certificates."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent;R=ROOT/'research'
sha=lambda b:hashlib.sha256(b).hexdigest()
def stable(x):
    if isinstance(x,dict):return {k:stable(v) for k,v in x.items() if k!='elapsed_seconds'}
    if isinstance(x,list):return [stable(v) for v in x]
    return x

def main():
    manifest=json.loads((ROOT/'RELEASE_MANIFEST.json').read_text())
    assert manifest['version']=='0.12.0' and len(manifest['files'])>70
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts and not p.is_relative_to(R/'results')}
    assert actual==set(manifest['files'])|{'RELEASE_MANIFEST.json'},sorted(actual-set(manifest['files'])-{'RELEASE_MANIFEST.json'})
    for name,h in manifest['files'].items():
        assert sha((ROOT/name).read_bytes())==h,name
        assert not any(x in name.lower() for x in ['manuscript','supplementary_information','typeset','editorial','complete.zip','completo.zip']),name
        assert Path(name).suffix.lower() not in {'.pdf','.tex','.docx','.doc','.zip','.tar','.gz'},name
    meta=json.loads((ROOT/'.zenodo.json').read_text());assert meta['license']=='MIT' and meta['version']=='0.12.0' and meta['upload_type']=='software'
    assert 'MIT' in (ROOT/'CITATION.cff').read_text()
    execution=json.loads((R/'results/EXECUTION.json').read_text());assert execution['status']=='PASS_EXACT_MATHEMATICAL_RESULTS' and len(execution['commands'])==11 and all(x['exit_code']==0 for x in execution['commands'])
    compared=[]
    for old in sorted((ROOT/'expected/core').iterdir()):
        fresh=R/'results'/old.name;assert fresh.is_file(),old.name
        if old.suffix=='.json':assert stable(json.loads(old.read_text()))==stable(json.loads(fresh.read_text())),old.name
        else:assert old.read_bytes()==fresh.read_bytes(),old.name
        compared.append(old.name)
    for prefix,folder in [('Data_S10_','supplement-v09/data'),('Data_S11_','supplement-v010/data'),('Data_S12_','supplement-v011/data'),('Data_S13_','supplement-v012/data')]:
        for old in sorted((R/folder).glob(prefix+'*')):
            name=old.name.removeprefix(prefix).upper().replace('.JSON','.json').replace('.CSV','.csv').replace('.TXT','.txt');fresh=R/'results'/name
            assert fresh.is_file(),name
            if old.suffix=='.json':assert stable(json.loads(old.read_text()))==stable(json.loads(fresh.read_text())),name
            else:assert old.read_bytes()==fresh.read_bytes(),name
            compared.append(name)
    audit=json.loads((R/'results/KINETIC_AUDIT.json').read_text());assert audit['status']=='PASS_CERTIFIED_CONTINUOUS_TIME_FD7_WITNESS'
    cert=json.loads((R/'results/DESIGN_CERTIFICATE.json').read_text());assert cert['status']=='PASS_CERTIFIED_DESIGN_FRONTIER'
    power=json.loads((R/'results/DESIGN_POWER.json').read_text());assert power['status']=='PASS_EXACT_DECLARED_POWER' and power['rows']==120
    tutorial=json.loads((R/'results/DESIGN_TUTORIAL.json').read_text());assert tutorial['fixed_horizon_design']['sufficient_blocks_certified']==200326
    assay=json.loads((R/'results/ASSAY_AUDIT.json').read_text());assert assay['status']=='PASS_FROZEN_TRAJECTORY_CAMPAIGN' and len(assay['power'])==72
    out=dict(assay_settings=72,design_contrast=cert['absolute_contrast'],power_rows=power['rows'],status='PASS_PUBLIC_CODE_DATA_REPRODUCTION',version='0.12.0',manifest_files=len(manifest['files']),compared_results=len(compared),compared_names=compared,kinetic_counts=audit['counts'],publication_scope='Software and mathematical data; manuscripts excluded',license='MIT')
    (R/'results/PUBLIC_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
