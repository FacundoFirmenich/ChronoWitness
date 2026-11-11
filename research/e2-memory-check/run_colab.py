"""Execute unchanged E1/E2 calculations with explicit verified Drive checkpoints."""
from pathlib import Path
import hashlib
import json
import os
import resource
import shutil
import subprocess
import sys
import time
import traceback
import urllib.request

HERE=Path(__file__).resolve().parent
DEST=Path(sys.argv[1]).resolve()
ARCHIVE_SHA='03a788ddeaa08d3b9ef1511208c8c37263cc5bd55af7e9b41f4f3068ab5ab529'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()

def copy_verified(source,target):
    target.parent.mkdir(parents=True,exist_ok=True)
    expected=sha(source)
    if target.exists():
        assert sha(target)==expected, f'Existing destination differs: {target}'
        return
    # Each run has a unique destination; do not overwrite another run's results.
    with source.open('rb') as inp,target.open('xb') as out:
        shutil.copyfileobj(inp,out,1024*1024)
    assert sha(target)==expected, f'Drive readback mismatch: {target}'

def checkpoint(label):
    target=DEST/label
    manifest={}
    for directory in ['benchmark_results','e2_results']:
        folder=HERE/directory
        if folder.exists():
            for f in sorted(folder.rglob('*')):
                if f.is_file():
                    rel=f.relative_to(HERE)
                    copy_verified(f,target/rel);manifest[str(rel)]=sha(f)
    for f in sorted(HERE.glob('*.py'))+sorted(HERE.glob('*PROTOCOL.json')):
        copy_verified(f,target/'source'/f.name);manifest['source/'+f.name]=sha(f)
    for name in ['SOURCE_MANIFEST.json','COLAB_RESULT.json']:
        f=HERE/name
        if f.exists():copy_verified(f,target/name);manifest[name]=sha(f)
    (target/'SHA256_READBACK.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'CHECKPOINT_VERIFIED {target}',flush=True)

def main():
    assert str(DEST).startswith('/content/drive/MyDrive/ChronoWitness/E2/'), DEST
    DEST.mkdir(parents=True,exist_ok=False)
    report=dict(status='RUNNING',platform='Google Colab CPU',stages=[],
        source_commit='3e5d45817e58f540f65fb196d1c878658eb28be2',
        memory_enforcement='No synthetic cgroup cap in Colab; records process RSS and assigned memory.',
        assigned_meminfo=Path('/proc/meminfo').read_text().splitlines()[:3],
        cpu_count=os.cpu_count(),cpu_affinity=sorted(os.sched_getaffinity(0)),
        python=sys.version,started_unix=time.time())
    begin=time.monotonic()
    try:
        import numpy as np
        import benchmark as e1
        # Data persist under the unique run path; future runs can reuse an explicitly supplied verified archive.
        archive=HERE/'datasets.zip'
        reuse=os.environ.get('CHRONOWITNESS_VERIFIED_ARCHIVE')
        t=time.monotonic()
        if reuse:
            source=Path(reuse);assert sha(source)==ARCHIVE_SHA
            copy_verified(source,archive)
        elif not archive.exists():
            assert shutil.disk_usage(HERE).free>2_000_000_000
            with urllib.request.urlopen('https://zenodo.org/api/records/8114649/files/datasets.zip/content',timeout=120) as r,archive.open('xb') as f:
                shutil.copyfileobj(r,f,1024*1024)
        assert archive.stat().st_size==357636847 and sha(archive)==ARCHIVE_SHA
        copy_verified(archive,DEST/'source_data/datasets.zip')
        report['stages'].append(dict(stage='download_verify_and_archive',seconds=time.monotonic()-t))
        # Run the original implementation in a child so its memory is released before E2.
        code="import benchmark as b; from pathlib import Path; b.download=lambda:(Path('datasets.zip'),'"+ARCHIVE_SHA+"'); b.main()"
        t=time.monotonic();subprocess.run([sys.executable,'-c',code],cwd=HERE,check=True)
        expected=json.loads((HERE/'reference_e1_metrics.json').read_text())
        observed=json.loads((HERE/'benchmark_results/METRICS.json').read_text())
        assert len(expected)==len(observed)==210
        for a,b in zip(expected,observed):
            for k in ['offset','horizon','date','split','model','n','predicted_negative','predicted_above_4095']:assert a[k]==b[k]
            for k in ['rmse','mae','bias']:assert np.isclose(a[k],b[k],rtol=1e-10,atol=1e-8)
        report['stages'].append(dict(stage='E1_refit_and_reference_check',seconds=time.monotonic()-t))
        checkpoint('01_E1_complete')
        t=time.monotonic();subprocess.run([sys.executable,str(HERE/'calibration.py'),str(archive)],cwd=HERE,check=True)
        report['stages'].append(dict(stage='E2_calibration',seconds=time.monotonic()-t))
        report['status']='COMPLETE_E1_E2_COLAB'
    except BaseException:
        report['status']='FAILED_OR_INTERRUPTED';report['error']=traceback.format_exc();raise
    finally:
        report['elapsed_seconds']=time.monotonic()-begin
        report['maximum_child_rss_kib']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        report['archive_sha256']=ARCHIVE_SHA
        (HERE/'COLAB_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
        checkpoint('02_final_or_failure')
        print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__': main()
