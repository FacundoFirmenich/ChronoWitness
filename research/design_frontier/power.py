"""Exact first-crossing power for declared iid two-point block laws, no sampling."""
from fractions import Fraction as F
from pathlib import Path
from math import comb
import json,csv,hashlib
P=Path(__file__).parent;R=P.parent;protocol=json.loads((P/'PROTOCOL.json').read_text())
def frontier(stakes,t,horizon):
    factors=[(1+q*(s-t)/(1+t),1+q*(-s-t)/(1+t)) for s in [1,-1] for q in stakes]
    powers=[([a**n for n in range(horizon+1)],[b**n for n in range(horizon+1)]) for a,b in factors]
    def evidence(n,k):return sum((a[k]*b[n-k] for a,b in powers),F(0))/len(powers)
    alive={0:1};hits=[];counts=[]
    for n in range(1,horizon+1):
        nextrow={}
        for k,c in alive.items():
            nextrow[k]=nextrow.get(k,0)+c;nextrow[k+1]=nextrow.get(k+1,0)+c
        hit={k:c for k,c in nextrow.items() if evidence(n,k)>=20}
        alive={k:c for k,c in nextrow.items() if k not in hit}
        hits.append(hit);counts.append(sum(alive.values()))
        assert sum(alive.values())+sum(sum(v.values())*2**(n-j-1) for j,v in enumerate(hits))==2**n
    return hits,counts,evidence

def main():
    rows=[];checks=0;N=protocol['power_horizon']
    for label,raw in enumerate(protocol['power_stakes']):
        stakes=list(map(F,raw))
        for t in map(F,protocol['power_tolerances']):
            hits,counts,evidence=frontier(stakes,t,N)
            # Independent exhaustive binary paths at horizon 10.
            paths={():[F(1)]*(2*len(stakes))};direct=[0]*10
            for n in range(1,11):
                new={}
                for path,capital in paths.items():
                    for x in [-1,1]:
                        updated=[c*(1+q*(s*x-t)/(1+t)) for c,(s,q) in zip(capital,[(s,q) for s in [1,-1] for q in stakes])]
                        assert sum(updated)/len(updated)==evidence(n,sum(v==1 for v in path)+(x==1));checks+=1
                        if sum(updated)/len(updated)>=20:direct[n-1]+=1
                        else:new[path+(x,)]=updated
                paths=new
            assert direct==[sum(v.values()) for v in hits[:10]]
            for prob in map(F,protocol['power_probabilities']):
                cumulative=F(0)
                for n,h in enumerate(hits,1):
                    cumulative+=sum((c*prob**k*(1-prob)**(n-k) for k,c in h.items()),F(0))
                    if abs(2*prob-1)<=t:assert cumulative<=F(1,20)
                    if n in [16,32,64,128,256]:rows.append(dict(mixture=label,tolerance=str(t),positive_probability=str(prob),mean=str(2*prob-1),blocks=n,crossing_probability=str(cumulative),decimal=float(cumulative),role='null' if abs(2*prob-1)<=t else 'alternative'))
    # Informative boundary: all factors are nonincreasing when t >= R = 1.
    for raw in protocol['power_stakes']:
        for q in map(F,raw):
            for s in [-1,1]:
                for x in [-1,1]:assert 0<=1+q*(s*x-1)/2<=1
    O=R/'results';O.mkdir(exist_ok=True)
    with (O/'DESIGN_POWER.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    out=dict(status='PASS_EXACT_DECLARED_POWER',horizon=N,rows=len(rows),independent_path_checks=checks,monte_carlo=False,biological_calibration=False,block_law='iid scores +1 with probability p and -1 otherwise',protocol_sha256=hashlib.sha256((P/'PROTOCOL.json').read_bytes()).hexdigest(),csv_sha256=hashlib.sha256((O/'DESIGN_POWER.csv').read_bytes()).hexdigest())
    (O/'DESIGN_POWER.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
