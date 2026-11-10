"""Exact global-in-time identities and certified readout-window bounds."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import csv,hashlib,json
from exp_polynomial import EP,rounded_interval
from moment_envelope import (propagate,drift,stationary,uniform_envelope,
    deterministic_initial,saturation_budget)
from independent_clusters import moments,reaction_generator

R=Path(__file__).resolve().parents[1];O=R/'results';O.mkdir(exist_ok=True)
lamgrid=(F(0),F(1,2),F(1),F(2));kgrid=(F(1,2),F(1),F(2));decay=(F(1),F(2),F(4))
initials=((0,0),(1,0),(0,2),(2,3));windows=tuple(product((0,1,4),(1,2,8)))
counts=dict(parameter_sets=0,initial_cases=0,global_moment_identities=0,ode_residual_identities=0,
    initial_identities=0,generator_component_identities=0,uniform_certificates=0,
    uniform_time_checks=0,windows=0,positive_window_budgets=0,
    equal_degradation_cases=0,double_degradation_cases=0,stationary_fano_checks=0,
    degradation_vs_deathfree_checks=0,rejected_invalid_contracts=0)
cases=[];rows=[];uniformrows=[]
case=0
for lam,k,g,d in product(lamgrid,kgrid,decay,decay):
    counts['parameter_sets']+=1
    for m,p in product(range(6),repeat=2):
        initial=deterministic_initial(m,p)
        assert reaction_generator(m,p,lam,k,g,d)==drift(initial,lam,k,g,d)
        counts['generator_component_identities']+=5
    if lam>0:
        v=stationary(lam,k,g,d)
        assert drift(v,lam,k,g,d)==(0,0,0,0,0)
        variance=v[1]+v[4]-v[1]**2
        assert variance/v[1]==1+k/(g+d) and variance>v[1]
        counts['stationary_fano_checks']+=1
        uniformrows.append((lam,k,g,d,*v,v[0]+v[2],v[1]+v[4],variance/v[1]))
    for m0,p0 in initials:
        case+=1;initial=deterministic_initial(m0,p0)
        y=propagate(initial,lam,k,g,d);oracle=moments(m0,p0,lam,k,g,d)
        rhs=drift(y,lam,k,g,d)
        for f,h,r,init in zip(y,oracle,rhs,initial):
            assert f==h,(lam,k,g,d,m0,p0,f.serial(),h.serial())
            assert f.derivative()==r and f.at_zero()==init
            counts['global_moment_identities']+=1;counts['ode_residual_identities']+=1;counts['initial_identities']+=1
        counts['initial_cases']+=1
        counts['equal_degradation_cases']+=g==d
        counts['double_degradation_cases']+=g==2*d
        eta=None;bound=None
        if lam>0:
            eta,bound=uniform_envelope(initial,lam,k,g,d)
            assert all(a<=b for a,b in zip(initial,bound))
            assert all(v<=0 for v in drift(bound,lam,k,g,d))
            counts['uniform_certificates']+=1
            for t in (0,1,2,4,8,12):
                for f,v in zip(y,bound):
                    assert f.log2_interval(t)[1]<=v,(case,t)
                    counts['uniform_time_checks']+=1
        cases.append((case,lam,k,g,d,m0,p0,eta if eta is not None else 'NOT_APPLICABLE_ZERO_IMMIGRATION'))
        for start,length in windows:
            end=start+length;raw,corr,radius=saturation_budget(y,start,end,8,32,k,g,d)
            assert 0<=raw<=corr and radius>32
            counts['windows']+=1;counts['positive_window_budgets']+=1
            q_m=y[0]+y[2];q_p=y[1]+y[4]
            qm=rounded_interval(q_m.log2_interval(end));qp=rounded_interval(q_p.log2_interval(end))
            rr=rounded_interval((raw,raw))[1];cc=rounded_interval((corr,corr))[1];rad=rounded_interval((radius,radius))[1]
            rows.append((case,start,end,8,32,*qm,*qp,rr,cc,rad))
        if m0==p0==0:
            # Explicit death-free translation is a valid but increasingly loose envelope.
            t=EP.term(0,1)
            deathfree= k*lam*t*t/2 + k*k*lam*t*t*t/3 + k*k*lam*lam*t*t*t*t/4
            q_p=y[1]+y[4]
            for time in (1,2,4,8,12):
                assert q_p.log2_interval(time)[1]<=deathfree.log2_interval(time)[0] if lam else q_p==0
                counts['degradation_vs_deathfree_checks']+=1

# Exact independent oracle at equal degradation, with one initial mRNA.
# At time log(2), kappa=2 and lambda=0, p=log(2), factorial second=2-2*log(2).
y=propagate(deterministic_initial(1,0),0,2,1,1)
assert y[1]==2*EP.term(1,1)
assert y[4]==8*(EP.term(1)-EP.term(2)-EP.term(2,1))
lo,hi=(y[4]-y[1]*y[1]).log2_interval(1)
assert lo>0
single=dict(time='log(2)',initial_mrna=1,initial_protein=0,immigration='0',translation='2',mrna_degradation='1',protein_degradation='1',protein_mean='log(2)',protein_factorial_second='2 - 2*log(2)',excess_variance_over_poisson_lower=str(rounded_interval((lo,hi))[0]),excess_variance_over_poisson_upper=str(rounded_interval((lo,hi))[1]))

invalid=[lambda:uniform_envelope((0,0,0,0,0),1,2,0,1),
         lambda:uniform_envelope((0,0,0,0,0),1,2,1,0),
         lambda:uniform_envelope((0,0,0,0,0),0,2,1,1),
         lambda:propagate((0,0,0,0),1,1,1,1),
         lambda:propagate((0,0,-1,0,0),1,1,1,1),
         lambda:deterministic_initial(F(1,2),0),
         lambda:saturation_budget(y,1,1,8,32,2,1,1),
         lambda:saturation_budget(y,0,1,0,32,2,1,1)]
for f in invalid:
    try:f()
    except ValueError:counts['rejected_invalid_contracts']+=1
    else:raise AssertionError('Invalid contract accepted')

def write(name,fields,values):
    with (O/name).open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(fields);writer.writerows(values)
write('TRANSLATION_CASES.csv',['case','immigration','translation','mrna_degradation','protein_degradation','initial_mrna','initial_protein','uniform_scale'],cases)
write('TRANSLATION_WINDOWS.csv',['case','start_log2','end_log2','mrna_cap','protein_cap','mrna_second_lower','mrna_second_upper','protein_second_lower','protein_second_upper','raw_arm_loss_upper','corrected_arm_loss_upper','corrected_contrast_radius_upper'],rows)
write('TRANSLATION_STATIONARY.csv',['immigration','translation','mrna_degradation','protein_degradation','mrna_mean','protein_mean','mrna_factorial_second','cross_moment','protein_factorial_second','mrna_second','protein_second','protein_fano'],uniformrows)
curve=[];base=propagate(deterministic_initial(0,0),1,2,1,1);t=EP.term(0,1)
deathfree=t*t+F(4,3)*t*t*t+t*t*t*t
for time in range(1,65):
    q=rounded_interval((base[1]+base[4]).log2_interval(time));q0=rounded_interval(deathfree.log2_interval(time))
    raw,corr,radius=saturation_budget(base,0,time,8,32,2,1,1)
    curve.append((time,*q,*q0,*[rounded_interval((x,x))[1] for x in (raw,corr,radius)]))
write('TRANSLATION_CURVES.csv',['time_log2','protein_second_lower','protein_second_upper','deathfree_second_lower','deathfree_second_upper','raw_arm_loss_upper','corrected_arm_loss_upper','corrected_contrast_radius_upper'],curve)
out=dict(status='PASS_EXACT_TRANSLATION_MOMENTS',biological_observations=False,monte_carlo=False,counts=counts,
    model='Explicit M immigration/degradation, catalytic protein production kappa*M, protein degradation; no burst approximation.',
    conditional_extension='Pathwise predictable rate bounds imply positive moment differential inequalities; the chemical mean-null hypotheses remain separate.',
    verification_independence='ODE recurrence and molecule-survival/Poisson-immigration formulas share only the rational exponential-polynomial ring. Direct reaction generator is independently evaluated. Proofs in S14 extend beyond the parameter grid.',
    single_mrna_counterexample=single,
    stationary_counterexample=dict(immigration=1,translation=2,mrna_degradation=1,protein_degradation=1,protein_mean='2',protein_variance='4',protein_second='8',poisson_second_with_same_mean='6'),
    source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))},
    csv_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.glob('TRANSLATION_*.csv'))})
(O/'TRANSLATION_MOMENTS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
