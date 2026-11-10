"""Exact delivered-input and switching-time robustness audit; no empirical data."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import csv,hashlib,json,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'finite_reporter'))
import exact_flow as flow
import independent_flow as ode
import kernels as K
import independent_envelope as ie
WORDS=['101111110010110010001000','100010110010111111001000']
VALUES=[Q(0),Q(1,4),Q(3,4),Q(1)]
SCENARIOS=['ideal','amplitude','delay','alternating_jitter','mixed','history_only']

def parameters(v,family,synthesis):
    alpha,beta=(1+v,1+3*v) if family==0 else (1+8*v,9-8*v)
    u0=v*v;u1=(1-v)**2 if synthesis else v*v+v+1
    return alpha,beta,u0,u1-u0

def matrix(v,family,synthesis,cascade):
    a,b,u,g=parameters(v,family,synthesis)
    m=[[0,0,0,0],[a,-a-b,0,0],[u,g,-8,0],[0,0,8,-7]] if cascade else [[0,0,0],[a,-a-b,0],[u,g,-7]]
    return [[Q(x) for x in row] for row in m]

def secondary_cycle(seq,mats):
    n=len(mats[0]);endcols=[];acols=[];bcols=[]
    interval=[]
    for mat in mats:
        interval.append([ode.step(mat,[Q(i==j) for i in range(n)]) for j in range(n)])
    for col in range(n):
        x=[Q(i==col) for i in range(n)];a=[Q(0)]*n;b=a[:]
        for z in seq:
            nxt=[sum(interval[z][j][0][i]*x[j] for j in range(n)) for i in range(n)]
            a=[a[i]+sum(interval[z][j][1][i]*x[j] for j in range(n)) for i in range(n)]
            b=[b[i]+sum(interval[z][j][2][i]*x[j] for j in range(n)) for i in range(n)]
            x=nxt
        endcols.append(x);acols.append(a);bcols.append(b)
    return tuple([list(row) for row in zip(*cols)] for cols in [endcols,acols,bcols])

def schedules(word,scenario):
    nominal=[int(z)*3 for z in word for _ in range(4)]
    switches=[j for j in range(1,96) if nominal[j]!=nominal[j-1]]
    shifted=[]
    for i,j in enumerate(switches):
        shift=1 if scenario=='delay' and i==0 else ((1 if i%2==0 else -1) if scenario in ['alternating_jitter','mixed'] else 0)
        shifted.append(j+shift)
    assert all(0<x<96 for x in shifted) and all(a<b for a,b in zip(shifted,shifted[1:]))
    delivered=[];timed=[]
    for j in range(96):
        count=sum(t<=j for t in shifted);z=nominal[0] if count%2==0 else 3-nominal[0]
        timed.append(z)
        delivered.append((1 if z==0 else 2) if scenario in ['amplitude','mixed','history_only'] else z)
    actual=delivered*3 if scenario!='history_only' else delivered+nominal*2
    timed_all=timed*3
    # Error decomposes into amplitude deviation and swept switching intervals.
    sweep=[Q(0)]*288
    for period in range(3):
        for a,b in zip(switches,shifted):
            for j in range(min(a,b),max(a,b)):sweep[period*96+j]+=1
    amp=[abs(VALUES[actual[j]]-VALUES[timed_all[j]]) for j in range(288)]
    error=[abs(VALUES[actual[j]]-VALUES[nominal[j%96]]) for j in range(288)]
    assert all(e<=a+s for e,a,s in zip(error,amp,sweep))
    return nominal,actual,error,amp,sweep

def window(cycles,initial,k,r):
    x=initial[:];a=[Q(0)]*len(x);b=a[:];start=None
    for j in range(k+r):
        p,i0,il=cycles[j]
        if j==k:start=x[:]
        if j>=k:
            a=[v+w for v,w in zip(a,flow.mv(i0,x))];b=[v+w for v,w in zip(b,flow.mv(il,x))]
        x=flow.mv(p,x)
    return start,x,a,b

def assert_abs(value,bound):
    assert ode.nonnegative(*K.sub(bound,value)) and ode.nonnegative(*K.add(bound,value))

def main():
    out=R/'results';out.mkdir(exist_ok=True);rows=[]
    counts=dict(flow_columns=0,kernel_crosschecks=0,windows=0,corrected_bounds=0,raw_bounds=0,amplitude_bounds=0,timing_budgets=0,resonant_windows=0,rejected_omitted_history=0)
    cycle_cache={}
    for case,(family,synthesis,cascade) in enumerate(product([0,1],[0,1],[False,True])):
        mats=[matrix(v,family,synthesis,cascade) for v in VALUES];maps=[flow.spectral(m) for m in mats];n=len(mats[0])
        gamma=Q(4 if cascade else 7);kappa=Q(2 if family==0 else gamma)
        weight=Q(2 if cascade else 1);g=weight*(1 if synthesis else 2);gl=g/(7*weight)
        lp=Q(3 if family==0 else 8);lu=weight*(2 if synthesis else 3);lul=lu/(7*weight)
        ell=[-Q(1,7)]*(n-2);weights=[Q(2),Q(1)] if cascade else [Q(1)]
        def cyc(seq):
            key=(case,tuple(seq))
            if key not in cycle_cache:
                a=flow.cycle(seq,maps);b=secondary_cycle(seq,mats);assert a==b
                cycle_cache[key]=a;counts['flow_columns']+=n
            return cycle_cache[key]
        for phase,wi in product([0,7],[0,1]):
            base=WORDS[wi];word=base[phase:]+base[:phase]
            for scenario in SCENARIOS:
                nom,actual,error,amp,sweep=schedules(word,scenario);ideal=cyc(nom);star=flow.periodic(ideal[0])
                pi0=flow.mv(ideal[1],star);pil=flow.mv(ideal[2],star)
                cycles=[cyc(actual[j*96:(j+1)*96]) for j in range(3)]
                dp=[];du=[]
                for j,z in enumerate(actual):
                    a,b,u,gs=parameters(VALUES[z],family,synthesis);aa,bb,uu,gg=parameters(VALUES[nom[j%96]],family,synthesis)
                    assert a>=0 and b>=0 and a+b>=kappa
                    dp.append(max(abs(a-aa),abs(b-bb)))
                    du.append(weight*max(abs(u-uu),abs(u+gs-uu-gg)))
                    assert dp[-1]<=lp*error[j] and du[-1]<=lu*error[j]
                for k,r in [(0,1),(1,1),(1,2)]:
                    t0=96*k;t1=96*(k+r)
                    pd=K.weighted(dp,kappa,t0,t1);pc=K.weighted(dp,gamma,t0,t1,kappa);ud=K.weighted(du,gamma,t0,t1)
                    ips,ipc=ie.integrate(dp,kappa,gamma,t0,t1);ius,_=ie.integrate(du,gamma,gamma,t0,t1)
                    assert pd==ips and pc==ipc and ud==ius;counts['kernel_crosschecks']+=3
                    epw=K.weighted(error,kappa,t0,t1);epc=K.weighted(error,gamma,t0,t1,kappa);euw=K.weighted(error,gamma,t0,t1)
                    direct=(Q(0),sum(du[t0:t1])/(7*weight))
                    timed=[a+s for a,s in zip(amp,sweep)]
                    for rate,other in [(kappa,None),(gamma,None),(gamma,kappa)]:
                        assert ode.nonnegative(*K.sub(K.weighted(timed,rate,t0,t1,other),K.weighted(error,rate,t0,t1,other)))
                        counts['timing_budgets']+=1
                    for initial_name in ['periodic','zero','one']:
                        init=star[:] if initial_name=='periodic' else [Q(1)]+[Q(initial_name=='one')]*(n-1)
                        start,end,a,b=window(cycles,init,k,r)
                        raw=(a[-1]-r*pi0[-1],b[-1]-r*pil[-1])
                        corr=K.sub(raw,(sum(ell[j]*(end[j+2]-start[j+2]) for j in range(n-2)),Q(0)))
                        ep=abs(init[1]-star[1]);ex=sum(w*abs(init[j+2]-star[j+2]) for j,w in enumerate(weights))
                        cb=K.add(K.scale(K.initial(kappa,t0,t1),gl*ep),K.add(direct,K.scale(pd,gl)))
                        rb=K.add(K.scale(K.initial(gamma,t0,t1),ex),K.add(K.scale(K.initial_cascade(gamma,kappa,t0,t1),g*ep),K.add(ud,K.scale(pc,g))))
                        acb=K.add(K.scale(K.initial(kappa,t0,t1),gl*ep),K.add((Q(0),lul*sum(error[t0:t1])),K.scale(epw,gl*lp)))
                        arb=K.add(K.scale(K.initial(gamma,t0,t1),ex),K.add(K.scale(K.initial_cascade(gamma,kappa,t0,t1),g*ep),K.add(K.scale(euw,lu),K.scale(epc,g*lp))))
                        for val,bnd in [(corr,cb),(raw,rb),(corr,acb),(raw,arb)]:assert_abs(val,bnd)
                        counts['windows']+=1;counts['corrected_bounds']+=1;counts['raw_bounds']+=1;counts['amplitude_bounds']+=2;counts['resonant_windows']+=int(gamma==kappa)
                        if scenario=='ideal' and initial_name=='periodic':assert raw==corr==K.ZERO
                        if scenario=='history_only' and initial_name=='periodic' and k==1 and family==1:
                            assert sum(error[t0:t1])==0 and corr!=K.ZERO and raw!=K.ZERO
                            counts['rejected_omitted_history']+=1
                        rows.append([case,family,synthesis,int(cascade),wi,phase,scenario,initial_name,k,r,*map(str,raw),*map(str,corr),*map(str,cb),*map(str,rb),*map(str,acb),*map(str,arb)])
    # Exact adverse example: difference exposure unchanged, nonlinear synthesis differs.
    a=list(map(int,WORDS[0]));b=list(map(int,WORDS[1]));hamming=sum(x!=y for x,y in zip(a,b))
    delivered_a=[2*x for x in a];delivered_b=[x+y for x,y in zip(a,b)]
    assert [x-y for x,y in zip(a,b)]==[x-y for x,y in zip(delivered_a,delivered_b)]
    changed=sum(x*x-y*y for x,y in zip(delivered_a,delivered_b))
    assert sum(a)==sum(b) and changed==hamming>0
    path=out/'INPUT_ROBUSTNESS_WINDOWS.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['case','rate_family','synthesis_family','maturation','schedule','phase','scenario','initial','discarded_periods','measured_periods','raw_a','raw_b','corrected_a','corrected_b','coefficient_corrected_bound_a','coefficient_corrected_bound_b','coefficient_raw_bound_a','coefficient_raw_bound_b','amplitude_corrected_bound_a','amplitude_corrected_bound_b','amplitude_raw_bound_a','amplitude_raw_bound_b']);writer.writerows(rows)
    source_paths=[Path(__file__),Path(__file__).with_name('kernels.py'),Path(__file__).with_name('independent_envelope.py'),R/'finite_reporter/exact_flow.py',R/'finite_reporter/independent_flow.py']
    report=dict(status='PASS_EXACT_INPUT_ROBUSTNESS',counts=counts,domain=dict(cases=8,inputs=[str(v) for v in VALUES],symbol_duration='4 log(2)',phases=[0,7],scenarios=SCENARIOS,initial=['periodic','zero','one'],windows=[[0,1],[1,1],[1,2]],rate_families=['alpha=1+v, beta=1+3v','alpha=1+8v, beta=9-8v'],synthesis_families=['u0=v^2, u1=v^2+v+1','u0=v^2, u1=(1-v)^2'],reporter='scalar decay 7 or maturation 8 then mature decay 7; no immature degradation'),
        common_mode_counterexample=dict(hamming_distance=hamming,unchanged_difference=True,synthesis_mean_contrast=str(Q(changed,24)),corrected_reporter_contrast='synthesis_mean_contrast / delta',empirical=False),
        scope='Exact mathematical inputs; finite-grid implementation checks accompany general proofs. Acquisition window is fixed on a common physical time axis. No statistical decision or calibration inferred.',
        independence='Spectral projectors vs componentwise ODE interval construction; closed acquisition primitives vs differential-equation error-filter recurrence.',
        source_sha256={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},csv_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (out/'INPUT_ROBUSTNESS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
