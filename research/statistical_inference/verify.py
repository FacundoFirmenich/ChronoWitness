"""Exact finite-law audit; no Monte Carlo or empirical biological observations."""
from fractions import Fraction as F
from itertools import product, combinations
from pathlib import Path
import csv,hashlib,json,time
from betting import STAKES,initial,update,evidence,endpoint_box_budget,randomized_pair_tolerance
from independent_paths import capital_from_counts,first_cross_counts
R=Path(__file__).resolve().parents[1];OUT=R/'results'

def finite_law_vertices(support,tolerance):
    vertices=set()
    for j,x in enumerate(support):
        if abs(x)<=tolerance:vertices.add(tuple(F(i==j) for i in range(len(support))))
    for j,k in combinations(range(len(support)),2):
        for mean in (-tolerance,tolerance):
            p=(support[k]-mean)/(support[k]-support[j])
            if 0<=p<=1:
                v=[F(0)]*len(support);v[j]=p;v[k]=1-p;vertices.add(tuple(v))
    return vertices

def enumerate_law(name,horizon,alpha):
    leaves=0;nodes=0;local_checks=0;crossed=F(0);mass=F(0);terminal=F(0);count_checks=0
    def visit(path,prob,capital,hit):
        nonlocal leaves,nodes,local_checks,crossed,mass,terminal,count_checks
        n=len(path)
        if name in ('fair','boundary','alternating'):
            t=F(0) if name=='fair' else F(1,4)
            radius=F(1)
            mean=t if name!='alternating' or n%2==0 else -t
        elif name=='adaptive':
            radius=F(2) if path and path[-1]>0 else F(1)
            t=radius/4;mean=t if not path or path[-1]>0 else -t
        elif name=='uninformative':radius=F(1);t=F(1);mean=F(1)
        else:raise ValueError(name)
        if name in ('fair','boundary'):
            assert evidence(capital)==capital_from_counts(n,sum(x>0 for x in path),t,STAKES)
            count_checks+=1
        if n==horizon:
            leaves+=1;mass+=prob;terminal+=prob*evidence(capital)
            if hit:crossed+=prob
            return
        nodes+=1;p=(1+mean/radius)/2
        options=[(-radius,1-p),(radius,p)]
        avg=[F(0)]*len(capital)
        for x,weight in options:
            new=update(capital,x,radius,t)
            for j,c in enumerate(new):avg[j]+=weight*c
            if weight:visit(path+(x,),prob*weight,new,hit or evidence(new)>=1/alpha)
        assert all(a<=c for a,c in zip(avg,capital));local_checks+=len(capital)
    visit((),F(1),initial(),False)
    assert mass==1 and terminal<=1 and crossed<=alpha
    return dict(law=name,horizon=horizon,alpha=str(alpha),leaves=leaves,nodes=nodes,local_component_checks=local_checks,
                count_product_checks=count_checks,first_cross_probability=str(crossed),terminal_mean_e=str(terminal))

def main():
    started=time.monotonic();OUT.mkdir(exist_ok=True)
    vertex_checks=0
    support=tuple(map(F,[-2,-1,0,1,2]))
    for t in (F(0),F(1,4),F(1),F(2)):
        for probabilities in finite_law_vertices(support,t):
            assert sum(probabilities)==1 and abs(sum(p*x for p,x in zip(probabilities,support)))<=t
            for s,q in product((1,-1),STAKES):
                factors=[1+q*(s*x-t)/(2+t) for x in support]
                assert min(factors)>=0 and sum(p*f for p,f in zip(probabilities,factors))<=1
                vertex_checks+=1
    # Full paths, including non-iid and history-dependent laws satisfying the conditional null.
    cases=[enumerate_law(name,10,a) for name,a in product(('fair','boundary','alternating','adaptive','uninformative'),(F(1,5),F(1,20)))]
    # Independent integer path-counting at every horizon, also for the invalid repeated p-test.
    valid=first_cross_counts(64,F(1,20),F(0),STAKES)
    peek=first_cross_counts(64,F(1,20),F(0),STAKES,exact_binomial=True)
    assert all(p<=F(1,20) for p in valid) and peek[-1]>F(1,20)
    assert valid[9]==F(next(c['first_cross_probability'] for c in cases if c['law']=='fair' and c['alpha']=='1/20'))
    # Sharp box support checked independently at every corner, including common and anticorrelated errors.
    corners=0;box_cases=0
    for ell,H,eps in product(((F(-1),),(F(-1,2),F(-1))), (F(1),F(3)), (F(0),F(1,10))):
        d=len(ell);start=(F(1,5),)*d;end=(F(1,4),)*d
        bound=endpoint_box_budget(ell,H,eps,start,end)
        g=(F(1),)+tuple(v/H for v in ell)+tuple(-v/H for v in ell)
        radii=(eps,)+start+end
        vals=[sum(c*r*sign for c,r,sign in zip(g,radii,sg)) for sg in product((-1,1),repeat=len(g))]
        assert max(vals)==bound and min(vals)==-bound
        corners+=len(vals);box_cases+=1
    # Randomization bridge exhausts arbitrary baselines and extremal errors for four potential means.
    pair_checks=0
    for b1,b2 in product((F(-10),F(0),F(7)),repeat=2):
        budgets=(F(1,10),F(1,5),F(1,4),F(1,8));tol=randomized_pair_tolerance(budgets)
        for signs in product((-1,1),repeat=4):
            m1a,m1b,m2a,m2b=[base+sign*b for base,sign,b in zip((b1,b1,b2,b2),signs,budgets)]
            contrast=((m1a-m2b)+(m2a-m1b))/2
            assert abs(contrast)<=tol;pair_checks+=1
    # Six copies of one fair block always cross a nominal 5% threshold for stake one.
    duplicate=[]
    for x in (-1,1):
        c=initial((F(1),))
        for _ in range(6):c=update(c,x,1,0,(F(1),))
        duplicate.append(evidence(c))
    assert duplicate==[F(32),F(32)]
    assert evidence(update(initial((F(1),)),1,1,0,(F(1),)))==1
    chosen_mean=(F(2)+F(1))/2;assert chosen_mean>1
    latent_mean=F(2,3)*(-1)+F(1,3)*2;clipped_mean=F(2,3)*(-1)+F(1,3)*1
    assert latent_mean==0 and clipped_mean==F(-1,3)
    weights=(F(1),F(-1))
    covariance_variances=[]
    for correlation in (F(-1),F(0),F(1)):
        sigma=((F(1),correlation),(correlation,F(1)))
        covariance_variances.append(sum(weights[i]*sigma[i][j]*weights[j] for i,j in product(range(2),repeat=2)))
    assert covariance_variances==[F(4),F(2),F(0)]
    rejection_checks=0
    for args in [(0,0,0),(2,1,0),(0,1,-1)]:
        try:update(initial(),*args)
        except ValueError:rejection_checks+=1
        else:raise AssertionError('Invalid range/budget not rejected')
    with (OUT/'STATISTICAL_CASES.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
    with (OUT/'STATISTICAL_CROSSINGS.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['blocks','valid_e_process_first_cross_probability','uncorrected_repeated_exact_binomial_probability','alpha'])
        w.writerows((i+1,str(v),str(p),'1/20') for i,(v,p) in enumerate(zip(valid,peek)))
    out=dict(status='PASS_EXACT_STATISTICAL_INTERFACE',biological_observations=False,monte_carlo=False,
        domain=dict(laws=['fair','boundary','alternating','adaptive','uninformative'],path_horizon=10,alphas=['1/5','1/20'],stakes=list(map(str,STAKES)),counting_horizon=64,vertex_support=list(map(str,support)),vertex_tolerances=['0','1/4','1','2']),
        counts=dict(law_cases=len(cases),path_leaves=sum(c['leaves'] for c in cases),tree_nodes=sum(c['nodes'] for c in cases),local_component_checks=sum(c['local_component_checks'] for c in cases),count_product_checks=sum(c['count_product_checks'] for c in cases),vertex_checks=vertex_checks,box_cases=box_cases,box_corners=corners,randomized_pair_checks=pair_checks,rejected_invalid_contracts=rejection_checks),
        adverse=dict(duplicated_block=dict(copies=6,nominal_alpha='1/20',false_rejection_probability='1',wrong_e='32',one_block_e='1'),outcome_selected_stake=dict(expected_factor=str(chosen_mean)),clipping=dict(latent_mean='0',clipped_mean=str(clipped_mean),required_bias_allowance='1/3'),endpoint_covariance=dict(anticorrelated_variance='4',diagonal_only_variance='2',common_mode_variance='0'),repeated_fixed_test=dict(horizon=64,nominal_alpha='1/20',ever_reject=str(peek[-1])),valid_e_process=dict(horizon=64,ever_reject=str(valid[-1]))),
        cases=cases,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))},csv_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('STATISTICAL_*.csv')},elapsed_seconds=time.monotonic()-started)
    (OUT/'STATISTICAL_INFERENCE.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:out[k] for k in ['status','counts','adverse']},indent=2))
if __name__=='__main__':main()
