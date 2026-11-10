"""Reproduce paper mathematics on Linux with Python stdlib and a C++17 compiler."""
from pathlib import Path
import hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parent
def main():
    out=ROOT/'results';out.mkdir(exist_ok=True)
    pair=json.loads((ROOT/'sources/FD7_CERTIFICATE_v0.7.0.json').read_text())['pair']
    words=[pair['sequence_A'],pair['sequence_B']]
    records=[]
    commands=[
        (['g++','-O2','-std=c++17','analysis/audit_phase_ensemble.cpp','-o','results/phase'],None),
        (['./results/phase',*words],'PHASE_ENSEMBLE_CERTIFICATE.json'),
        ([sys.executable,'analysis/verify_phase_python.py'],None),
        ([sys.executable,'analysis/audit_design_structure.py'],None),
        (['g++','-O2','-std=c++17','analysis/audit_reader_instrument.cpp','-o','results/instrument'],None),
        (['./results/instrument',*words],'READER_INSTRUMENT_CERTIFICATE.json'),
        ([sys.executable,'analysis/verify_reader_instrument.py'],None),
        ([sys.executable,'analysis/audit_stochastic.py'],None),
        ([sys.executable,'analysis/audit_markov_boundary.py'],None),
        ([sys.executable,'analysis/verify_markov_boundary.py'],None),
        ([sys.executable,'analysis/audit_general_criterion.py'],None),
    ]
    manifest={'status':'RUNNING','python':platform.python_version(),'platform':platform.platform(),
      'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((ROOT/'analysis').glob('*')) if p.is_file()},'commands':records,
      'biological_validation':False,'external_peer_review':False}
    for cmd,destination in commands:
        start=time.monotonic()
        run=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
        records.append(dict(command=cmd,exit_code=run.returncode,elapsed_seconds=time.monotonic()-start,
                            stdout=run.stdout,stderr=run.stderr))
        if run.returncode:
            manifest['status']='FAIL'
            (out/'EXECUTION.json').write_text(json.dumps(manifest,indent=2)+'\n')
            raise RuntimeError(records[-1])
        if destination:
            (out/destination).write_text(json.dumps(json.loads(run.stdout),indent=2)+'\n')
    manifest['status']='PASS_EXACT_MATHEMATICAL_RESULTS'
    (out/'EXECUTION.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':manifest['status'],'commands':len(records)},indent=2))
if __name__=='__main__':main()
