"""Exact/certified mathematical audits; no Monte Carlo or biological data."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from math import comb
import csv,hashlib,json,sys
from envelopes import (compound_pgf_upper,compound_moments,geometric_pgf,
    pgf_stoploss,stoploss_bound,detector_contract,contrast_contract,
    score_clipping_bias,exp_interval)
from independent_laws import (compound_stoploss_interval,compound_coefficients,
    recursive_coefficients,negative_exp_interval)

R=Path(__file__).resolve().parents[1];O=R/'results';O.mkdir(exist_ok=True)
sys.path.insert(0,str(R/'statistical_inference'))
from betting import initial,update,evidence,STAKES
counts={}
rows=[];pgf_checks=0;coefficient_checks=0;exp_checks=0
U=(F(9,8),F(5,4),F(3,2),F(2),F(3))
thresholds=(F(0),F(1,2),F(1),F(2),F(4),F(8),F(12),F(16),F(24),F(32))
for mass,p in product((F(0),F(1,4),F(1),F(4)),(F(0),F(1,4),F(1,2))):
    a=compound_coefficients(mass,p,32);b=recursive_coefficients(mass,p,32)
    assert a==b;coefficient_checks+=len(a)
    for n0 in (0,1,4):
        mean,second=compound_moments(n0,mass,1/(1-p),(1+p)/(1-p)**2)
        pgfs=[(u,compound_pgf_upper(n0,mass,u,geometric_pgf(u,p))) for u in U if p*u<1]
        for cap in thresholds:
            lo,hi=compound_stoploss_interval(n0,mass,p,cap)
            bound=stoploss_bound(cap,mean,second,pgfs)
            assert 0<=lo<=hi<=bound,(n0,mass,p,cap,hi,bound)
            for u,m in pgfs:
                assert hi<=pgf_stoploss(cap,u,m);pgf_checks+=1
            rows.append((n0,mass,p,cap,lo,hi,bound,mean,second))
for x in (F(0),F(1,16),F(1,4),F(1),F(4),F(8),F(16)):
    a,b=exp_interval(x);c,d=negative_exp_interval(x)
    assert a<=1/d and b>=1/c and b-a<=F(2,10**24)
    exp_checks+=1
counts.update(compound_laws=36,stoploss_cases=len(rows),pgf_inequalities=pgf_checks,
              independent_coefficient_checks=coefficient_checks,exponential_crosschecks=exp_checks)

# Reaction algebra: every reachable state through six reaction events, using
# single/batch arrivals, deaths and all directed one-for-one conversions.
mass_checks=0;states_checked=0
for d in (1,2,3):
    for n0 in (0,1,2):
        states={(tuple([n0]+[0]*(d-1)),n0)}
        for step in range(6):
            new=set()
            for state,dom in states:
                assert sum(state)<=dom;states_checked+=1
                for j in range(d):
                    for batch in (1,3):
                        s=list(state);s[j]+=batch;new.add((tuple(s),dom+batch));mass_checks+=1
                    if state[j]:
                        s=list(state);s[j]-=1;new.add((tuple(s),dom));mass_checks+=1
                        for k in range(d):
                            if j!=k:
                                s=list(state);s[j]-=1;s[k]+=1;new.add((tuple(s),dom));mass_checks+=1
            assert all(sum(s)<=v for s,v in new);states=new
counts.update(reaction_states=states_checked,reaction_transitions=mass_checks)

# Deterministic box support of the saturated functional; endpoints may be
# arbitrarily dependent, and are not required to be attainable independently.
vertices=0;boxes=0
for d,h in product((1,2,3),(F(1),F(2))):
    c=tuple(F(j+1) for j in range(d));ell=tuple(F((-1)**j*(j+1),2) for j in range(d));caps=tuple(F(j+1) for j in range(d))
    lo,hi,bias=detector_contract(c,ell,h,caps,[F(0)]*d)
    vals=[]
    for bits in product((0,1),repeat=3*d):
        avg=[bits[j]*caps[j] for j in range(d)]
        start=[bits[d+j]*caps[j] for j in range(d)]
        end=[bits[2*d+j]*caps[j] for j in range(d)]
        v=sum(c[j]*avg[j]-ell[j]*(end[j]-start[j])/h for j in range(d))
        assert lo<=v<=hi;vals.append(v);vertices+=1
    assert min(vals)==lo and max(vals)==hi and bias==0;boxes+=1
counts.update(detector_boxes=boxes,detector_vertices=vertices)

# Explicit shared-path measurement distortion check, including endpoint signs.
path_checks=0
for h,cap in product((F(1),F(2)),(F(1),F(2),F(3))):
    for avg,start,end in product(map(F,range(5)),repeat=3):
        d=max(avg,start,end);loss=max(F(0),d-cap)
        lo,hi,bias=detector_contract([1],[-1],h,[cap],[loss])
        latent=avg+(end-start)/h
        observed=min(avg,cap)+(min(end,cap)-min(start,cap))/h
        assert abs(observed-latent)<=bias and lo<=observed<=hi;path_checks+=1
counts['detector_path_checks']=path_checks

# Hardware saturation changes an exact nonnegative equal-mean comparison:
# A=1, B=0 or 2 with equal probabilities, cap=1. The observed contrast is 1 or 0.
assert F(1)==(F(0)+2)/2
adverse=[]
capital_checks=0
def closed_capital(n,k,t):
    return sum((1+q*(s-t)/(1+t))**k*(1-q*t/(1+t))**(n-k)
               for s in (1,-1) for q in STAKES)/8
for n in range(1,25):
    for k in range(n+1):
        for t in (F(0),F(1,2)):
            capital=initial()
            for x in [0]*(n-k)+[1]*k:capital=update(capital,x,1,t)
            assert evidence(capital)==closed_capital(n,k,t);capital_checks+=1
for n in range(1,25):
    crossings=[0]*(n+1);alive={0:1}
    for step in range(1,n+1):
        nxt={}
        for k,num in alive.items():
            for x in (0,1):
                kk=k+x
                naive=sum(((1+q)**kk for q in STAKES),F(0))/8 + sum(((1-q)**kk for q in STAKES),F(0))/8
                # Zero observations multiply by one; count formula independent of update().
                if naive>=20:crossings[step]+=num
                else:nxt[kk]=nxt.get(kk,0)+num
        alive=nxt
    prob=sum(F(count,2**step) for step,count in enumerate(crossings))
    corrected_crossings=[0]*(n+1);alive={0:1}
    for step in range(1,n+1):
        nxt={}
        for k,num in alive.items():
            for x in (0,1):
                kk=k+x
                if closed_capital(step,kk,F(1,2))>=20:corrected_crossings[step]+=num
                else:nxt[kk]=nxt.get(kk,0)+num
        alive=nxt
    corrected=sum(F(count,2**step) for step,count in enumerate(corrected_crossings))
    assert corrected<=F(1,20)
    monotone_threshold=sum(F(comb(n,k),2**n) for k in range(n+1) if closed_capital(n,k,0)>=20)
    assert prob==monotone_threshold
    adverse.append((n,prob,corrected))
assert adverse[-1][1]>F(1,20)
counts['capital_product_crosschecks']=capital_checks
valid_local=0
for tolerance in (F(1,2),F(3,4),F(1)):
    for radius in (F(1),F(2)):
        caps=[update(initial(),F(x),radius,tolerance) for x in (0,1)]
        assert all((a+b)/2<=1 for a,b in zip(*caps));valid_local+=len(caps[0])
counts['saturation_null_component_checks']=valid_local

# First moment alone: increasingly rare large counts retain mean one.
rare=[]
for k in (2,4,16,64,256):
    loss=1-F(1,k);assert loss>=F(1,2);rare.append(dict(large_count=k,probability=str(F(1,k)),mean='1',cap='1',loss=str(loss)))
for n in range(0,41):
    for cap in range(1,21):
        assert max(F(0),n-cap)<=F(n*n,4*cap)
counts['quadratic_pointwise_checks']=41*20

invalid=0
for thunk in [lambda:geometric_pgf(2,F(1,2)),lambda:geometric_pgf(1,0),
              lambda:compound_pgf_upper(-1,1,2,2),lambda:compound_pgf_upper(0,-1,2,2),
              lambda:pgf_stoploss(-1,2,2),lambda:score_clipping_bias(1,1,2,lambda r:1),
              lambda:detector_contract([1],[-1],0,[1],[1]),
              lambda:detector_contract([-1],[-1],1,[1],[1]),
              lambda:contrast_contract((0,1,0),(0,1,0),0,0,1)]:
    try:thunk()
    except ValueError:invalid+=1
    else:raise AssertionError('Invalid contract accepted')
counts['rejected_invalid_contracts']=invalid
structural=[]
for name,initial_population,actual_added,envelope_initial,envelope_added in [
        ('ignored_initial_count',1,0,0,0),
        ('translation_without_envelope',1,1,1,0),
        ('batch_treated_as_single_arrival',0,3,0,1)]:
    actual=initial_population+actual_added
    wrong=envelope_initial+envelope_added
    assert actual>wrong
    structural.append(dict(case=name,actual=actual,invalid_envelope=wrong))

def write(name,fields,rows):
    with (O/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(fields);w.writerows(rows)
write('COUNT_TAIL_CASES.csv',['initial_cap','arrival_mass','geometric_p','cap','stoploss_lower','stoploss_upper','certified_bound','first_moment','second_moment'],rows)
write('SATURATION_CROSSINGS.csv',['blocks','naive_first_cross_probability','bias_qualified_first_cross_probability'],adverse)
curve=[]
for p in (F(0),F(1,4),F(1,2)):
    mean,second=compound_moments(0,1,1/(1-p),(1+p)/(1-p)**2)
    pgfs=[(u,compound_pgf_upper(0,1,u,geometric_pgf(u,p))) for u in U if p*u<1]
    for cap in range(1,41):
        low,high=compound_stoploss_interval(0,1,p,cap)
        curve.append((p,cap,low,high,stoploss_bound(cap,mean,second,pgfs),second/(4*cap)))
write('COUNT_TAIL_CURVES.csv',['geometric_p','cap','stoploss_lower','stoploss_upper','certified_bound','second_moment_bound'],curve)
out=dict(status='PASS_CERTIFIED_COUNT_TAILS',monte_carlo=False,biological_observations=False,
    arithmetic='Exact rational operations and outward-rounded rigorous exponential intervals; 24 decimal places.',counts=counts,
    chemical_scope='Nonbranching conversions/death plus dominated immigration batches; initial population must be covered. Explicit translation branching is not automatically covered.',
    saturation_counterexample=dict(latent_means=['1','1'],saturated_means=['1','1/2'],mean_contrast='1/2',naive_false_reject_by_24=str(adverse[-1][1]),qualified_false_reject_by_24=str(adverse[-1][2]),corrected_tolerance='1/2'),
    rare_count_controls=rare,
    structural_adverse_controls=structural,
    source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))},
    csv_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.glob('COUNT_TAIL_*.csv'))+sorted(O.glob('SATURATION_CROSSINGS.csv'))})
(O/'COUNT_TAILS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2))
