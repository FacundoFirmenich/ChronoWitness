"""Numerical finite-window Markov reward moments and linear-reporter means.

Matrix-exponential propagation is checked against independent ODE integration.
These are numerical references, not interval certificates of second moments.
"""
from pathlib import Path
from fractions import Fraction as F
import json, hashlib
import numpy as np
from scipy.linalg import expm
from scipy.integrate import solve_ivp

P=Path(__file__).resolve().parent; R=P.parent; O=R/'results'; O.mkdir(exist_ok=True)
protocol=json.loads((P/'PROTOCOL.json').read_text())

def models():
    null=[np.array([[-.75,.75],[.25,-.25]]),np.array([[-.5,.5],[1.5,-1.5]])]
    cert=json.loads((R/'supplement-v011/data/Data_S12_design_certificate.json').read_text())
    alternative=[np.array([[float(F(v)) for v in row] for row in q]) for q in cert['generators']]
    return [('two_state_null',null),('certified_three_state',alternative)]

def periodic(qs,word):
    trans=[expm(q) for q in qs]; b=np.eye(len(qs[0]))
    for z in map(int,word):b=b@trans[z]
    a=b.T-np.eye(len(b));a[-1]=1;rhs=np.zeros(len(b));rhs[-1]=1
    p=np.linalg.solve(a,rhs)
    # Markov tree formula is independent of the linear stationary solver.
    if len(p)==2:tree=np.array([b[1,0],b[0,1]])
    else:
        tree=[]
        for i in range(3):
            j,k=[v for v in range(3) if v!=i]
            tree.append(b[j,i]*b[k,i]+b[j,i]*b[k,j]+b[j,k]*b[k,i])
        tree=np.array(tree)
    tree/=tree.sum()
    assert np.max(abs(tree-p))<2e-13 and min(p)>0 and np.max(abs(p@b-p))<2e-13
    return p

def propagate(blocks,word,periods,p):
    n=len(p);state=np.r_[p,np.zeros(2*n)];ode=state.copy();trans=[expm(b) for b in blocks]
    for z in map(int,word*periods):
        state=state@trans[z]
        solution=solve_ivp(lambda t,v:v@blocks[z],(0,1),ode,method='DOP853',rtol=2e-12,atol=2e-13)
        assert solution.success;ode=solution.y[:,-1]
    error=float(np.max(abs(state-ode)));assert error<2e-8,error
    return state,error

def main():
    records=[];initials=[];errors=[]
    for name,qs in models():
        n=len(qs[0]);d=np.diag([1]+[0]*(n-1));zero=np.zeros((n,n));ps=[]
        for arm,word in enumerate(protocol['words']):
            p=periodic(qs,word);ps.append(p.tolist())
            reward=[np.block([[q,d,zero],[zero,q,2*d],[zero,zero,q]]) for q in qs]
            for periods in protocol['windows_periods']:
                h=24*periods;v,error=propagate(reward,word,periods,p);errors.append(error)
                mean=float(v[n:2*n].sum()/h);second=float(v[2*n:].sum()/h**2)
                assert 0<mean<1 and mean**2<second<mean
                row=dict(model=name,arm=arm,periods=periods,mean=mean,second_moment=second,variance=second-mean**2,reporters=[])
                for raw in protocol['reporter_rates']:
                    g=float(F(raw));blocks=[np.block([[q,g*d,zero],[zero,q-g*np.eye(n),np.eye(n)],[zero,zero,q]]) for q in qs]
                    v,error=propagate(blocks,word,periods,p);errors.append(error)
                    end=float(v[n:2*n].sum());avg=float(v[2*n:].sum()/h)
                    assert abs(avg+end/(g*h)-mean)<2e-12
                    row['reporters'].append(dict(rate=raw,raw_mean=avg,endpoint_mean=end,corrected_mean=avg+end/(g*h)))
                records.append(row)
        initials.append(dict(model=name,generators=[q.tolist() for q in qs],initial=ps))
    for periods in protocol['windows_periods']:
        for name,_ in models():
            pair=[r for r in records if r['model']==name and r['periods']==periods];delta=pair[0]['mean']-pair[1]['mean']
            if name=='two_state_null':assert abs(delta)<2e-13
            else:assert abs(delta-.010079470547504152)<2e-13
    out=dict(status='PASS_NUMERICAL_MOMENT_REFERENCES',method='Block matrix exponential independently checked by DOP853; stationary linear solve checked by tree formula',maximum_ode_difference=max(errors),records=records,models=initials,protocol_sha256=hashlib.sha256((P/'PROTOCOL.json').read_bytes()).hexdigest())
    (O/'ASSAY_MOMENTS.json').write_text(json.dumps(out,indent=2)+'\n')
    # Small text interface avoids a third-party JSON dependency in the C++ simulator.
    lines=[str(len(initials))]
    for model in initials:
        n=len(model['initial'][0]);lines.append(str(n))
        for q in model['generators']:lines.extend(' '.join(format(v,'.17g') for v in row) for row in q)
        lines.extend(' '.join(format(v,'.17g') for v in p) for p in model['initial'])
    (O/'ASSAY_MODELS.txt').write_text('\n'.join(lines)+'\n')
    print(json.dumps(dict(status=out['status'],maximum_ode_difference=max(errors),records=len(records)),indent=2))
if __name__=='__main__':main()
