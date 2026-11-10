"""Run the frozen event-driven assay campaign and report simulation uncertainty."""
from pathlib import Path
from fractions import Fraction as F
import subprocess,sys,json,hashlib,csv,math,time
from scipy.stats import beta
P=Path(__file__).resolve().parent;R=P.parent;O=R/'results';O.mkdir(exist_ok=True)

def cp(k,n,alpha):
    return [0. if k==0 else float(beta.ppf(alpha/2,k,n-k+1)),1. if k==n else float(beta.ppf(1-alpha/2,k+1,n-k))]

def main():
    start=time.perf_counter();q=json.loads((P/'PROTOCOL.json').read_text())
    subprocess.run([sys.executable,str(P/'moments.py')],check=True)
    subprocess.run([sys.executable,str(P/'calibration.py')],check=True)
    header=['#pragma once', 'const std::string WORDS[2]={'+','.join(json.dumps(x) for x in q['words'])+'};']
    for name,key in [('VALIDATION_SEEDS','validation_seeds'),('POWER_SEEDS','power_seeds')]:header.append('const uint64_t '+name+'[]={'+','.join(str(v)+'ULL' for v in q[key])+'};')
    for name,key in [('VALIDATION_N','validation_per_seed'),('POWER_REPLICATES','power_replicates_per_seed'),('BENCHMARK_N','benchmark_replicates'),('BENCHMARK_SEED','benchmark_seed')]:header.append(f'const int {name}={q[key]};')
    for name,key in [('GAMMAS','reporter_rates'),('TOLERANCES','power_tolerances'),('BENCHMARK_P','benchmark_probabilities'),('BENCHMARK_T','benchmark_tolerances')]:header.append('const double '+name+'[]={'+','.join(repr(float(F(v))) for v in q[key])+'};')
    header.append('const int HORIZONS[]={'+','.join(map(str,q['power_horizons']))+'};')
    header.append('const std::vector<std::vector<double>> STAKES={'+','.join('{'+','.join(repr(float(F(v))) for v in group)+'}' for group in q['power_stakes'])+'};')
    (O/'assay_config.hpp').write_text('\n'.join(header)+'\n')
    compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0]
    subprocess.run(['g++','-O3','-std=c++17','-Wall','-Wextra','-Werror','-I',str(O),str(P/'simulate.cpp'),'-o',str(O/'assay_simulate')],check=True)
    subprocess.run([str(O/'assay_simulate'),str(O/'ASSAY_MODELS.txt'),str(O)],check=True)
    refs=json.loads((O/'ASSAY_MOMENTS.json').read_text());raw=list(csv.DictReader((O/'ASSAY_VALIDATION_RAW.csv').open()));checks=[]
    fields=['mean','second_moment','raw_slow','raw_fast','endpoint_slow','endpoint_fast'];m=len(raw)*len(fields)
    for row in raw:
        target=next(v for v in refs['records'] if v['model']==q['models'][int(row['model'])] and v['periods']==int(row['periods']) and v['arm']==int(row['arm']))
        expected=[target['mean'],target['second_moment'],*[r['raw_mean'] for r in target['reporters']],*[r['endpoint_mean'] for r in target['reporters']]]
        tolerance=math.sqrt(math.log(4*m/float(F(q['validation_error_budget'].split()[0])))/(2*int(row['replicates'])))
        for key,value in zip(fields,expected):
            error=abs(float(row[key])-value);checks.append(dict(model=target['model'],seed=row['seed'],periods=target['periods'],arm=target['arm'],quantity=key,reference=value,estimate=float(row[key]),absolute_error=error,simultaneous_hoeffding_radius=tolerance,passed=error<=tolerance+2e-10))
    # Same first-crossing engine checked against pre-existing exact probabilities.
    exact=list(csv.DictReader((R/'supplement-v011/data/Data_S12_design_power.csv').open()));bench=[]
    for row in csv.DictReader((O/'ASSAY_BENCHMARK_RAW.csv').open()):
        p,t=float(row['probability']),float(row['tolerance']);match=next(r for r in exact if r['mixture']=='0' and int(r['blocks'])==256 and abs(float(F(r['positive_probability']))-p)<1e-12 and abs(float(F(r['tolerance']))-t)<1e-12)
        estimate=int(row['crossings'])/int(row['replicates']);truth=float(F(match['crossing_probability']));bound=math.sqrt(math.log(16/float(F(q['validation_error_budget'].split()[0])))/(2*int(row['replicates'])))
        bench.append(dict(**row,estimate=estimate,exact_probability=truth,hoeffding_radius=bound,passed=abs(estimate-truth)<=bound))
    groups={}
    for row in csv.DictReader((O/'ASSAY_POWER_RAW.csv').open()):
        key=tuple(row[k] for k in ['model','periods','mixture','tolerance','horizon']);groups.setdefault(key,[]).append(row)
    powers=[]
    for key,seeds in sorted(groups.items()):
        k=sum(int(s['crossings']) for s in seeds);n=sum(int(s['replicates']) for s in seeds);assert len(seeds)==len(q['power_seeds'])
        powers.append(dict(model=q['models'][int(key[0])],periods=int(key[1]),mixture=int(key[2]),tolerance=float(key[3]),horizon=int(key[4]),crossings=k,replicates=n,estimate=k/n,pointwise_95=cp(k,n,.05),simultaneous_95=cp(k,n,.05/len(groups)),seed_counts=[dict(seed=s['seed'],crossings=int(s['crossings']),replicates=int(s['replicates'])) for s in seeds]))
    assert len(powers)==72
    out=dict(status='PASS_FROZEN_TRAJECTORY_CAMPAIGN' if all(c['passed'] for c in checks+bench) else 'REFERENCE_ENVELOPE_FAILURE_RETAINED',protocol_sha256=hashlib.sha256((P/'PROTOCOL.json').read_bytes()).hexdigest(),moments=checks,exact_power_benchmarks=bench,power=powers,monte_carlo=True,biological_observations=False,compiler=compiler,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(P.iterdir()) if p.suffix in {'.py','.cpp','.json'}},output_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.glob('ASSAY*')) if p.suffix in {'.csv','.json','.txt'} and p.name!='ASSAY_AUDIT.json'},elapsed_seconds=time.perf_counter()-start)
    (O/'ASSAY_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(status=out['status'],moment_checks=len(checks),benchmark_cases=len(bench),power_rows=len(powers),elapsed_seconds=out['elapsed_seconds']),indent=2))
    assert out['status']=='PASS_FROZEN_TRAJECTORY_CAMPAIGN', 'Retain failed campaign outputs; investigate before any rerun.'
if __name__=='__main__':main()
