"""Measure the complete real workload using kernel cgroup counters and process RSS."""
from pathlib import Path
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE/'resource_results'
CG = Path('/sys/fs/cgroup')

def counter(name):
    return (CG/name).read_text().strip()

def stage(script, *args):
    start=time.monotonic()
    r=subprocess.run([sys.executable,str(HERE/script),*args],cwd=HERE)
    return dict(script=script,returncode=r.returncode,elapsed_seconds=time.monotonic()-start,
        cgroup_memory_peak_bytes=int(counter('memory.peak')),
        maximum_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)

def main():
    OUT.mkdir(exist_ok=True)
    p=json.loads((HERE/'E2_PROTOCOL.json').read_text())
    limit=int(counter('memory.max')); swap=int(counter('memory.swap.max'))
    preflight=dict(memory_max=limit,swap_max=swap,cpu_max=counter('cpu.max'),
        page_size=os.sysconf('SC_PAGE_SIZE'),requested_memory=p['resource_gate']['memory_limit_bytes'])
    (OUT/'PREFLIGHT.json').write_text(json.dumps(preflight,indent=2)+'\n')
    print(json.dumps(preflight),flush=True)
    # Linux rounds byte limits down to a whole memory page; never accept a larger limit.
    requested=p['resource_gate']['memory_limit_bytes']
    assert 0 <= requested-limit < preflight['page_size'] and swap==0, preflight
    quota,period=map(int,counter('cpu.max').split());assert quota/period==2
    start=time.monotonic();stages=[]; verified=False
    try:
        stages.append(stage('benchmark.py'))
        assert stages[-1]['returncode']==0
        expected=json.loads((HERE/'reference_e1_metrics.json').read_text())
        observed=json.loads((HERE/'benchmark_results/METRICS.json').read_text())
        assert len(expected)==len(observed)==210
        for a,b in zip(expected,observed):
            for k in ['offset','horizon','date','split','model','n']: assert a[k]==b[k]
            for k in ['rmse','mae','bias']:
                assert np.isclose(a[k],b[k],rtol=1e-10,atol=1e-8),(k,a[k],b[k])
            for k in ['predicted_negative','predicted_above_4095']: assert a[k]==b[k]
        verified=True
        stages.append(stage('calibration.py','/tmp/chronowitness-E1-datasets.zip'))
        assert stages[-1]['returncode']==0
    finally:
        events={k:int(v) for k,v in (line.split() for line in counter('memory.events').splitlines())}
        complete=verified and len(stages)==2 and all(x['returncode']==0 for x in stages)
        report=dict(status='PASS_3GB_NO_SWAP_REAL_E1_E2' if complete and events.get('oom',0)==0 else 'FAIL_OR_INCOMPLETE',
            source_commit=os.environ.get('GITHUB_SHA'),memory_limit_bytes=limit,swap_limit_bytes=swap,
            cpu_quota=counter('cpu.max'),memory_peak_bytes=int(counter('memory.peak')),
            memory_current_bytes=int(counter('memory.current')),memory_events=events,
            maximum_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            measured_pipeline_seconds=time.monotonic()-start,stages=stages,e1_reference_reproduction=verified,
            protocol_sha256=hashlib.sha256((HERE/'E2_PROTOCOL.json').read_bytes()).hexdigest(),
            scope='Cgroup peak includes workload and container cache/setup; RSS is largest child process. This is a constrained GitHub runner, not a qBraid session. Excludes Jupyter and qBraid base services.',
            source_files_sha256={n:hashlib.sha256((HERE/n).read_bytes()).hexdigest() for n in ['benchmark.py','calibration.py','measure.py','E2_PROTOCOL.json','BENCHMARK_PROTOCOL.json']})
        (OUT/'RESOURCE_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2),flush=True)
    assert report['status']=='PASS_3GB_NO_SWAP_REAL_E1_E2'

if __name__=='__main__': main()
