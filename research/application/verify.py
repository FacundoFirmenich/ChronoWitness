"""Check stimulation integrity and score analysis against exact path capital."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json,math,hashlib
from plan import rows,WORDS
from analyze import evaluate

def main():
    data=list(rows(24,1,2,1,618));assert len(data)==3456
    for block in range(1,25):
        subset=[r for r in data if r['block']==block]
        for arm in 'ab':
            rs=[r for r in subset if r['schedule']==arm];assert len(rs)==72
            phase=rs[0]['phase'];word=WORDS['ab'.index(arm)];expected=(word[phase:]+word[:phase])*3
            assert ''.join(str(r['input']) for r in rs)==expected
            assert sum(r['stage']=='acquisition' for r in rs)==48
    checked=0
    for path in product([-1,1],repeat=9):
        for tolerance in [F(0),F(1,10)]:
            result=evaluate([dict(block_id=str(i),score=x,mean_tolerance=float(tolerance),support_radius=1) for i,x in enumerate(path)])
            exact=[]
            for s,q in product([1,-1],[F(1,8),F(1,4),F(1,2),F(1)]):
                c=F(1)
                for x in path:c*=1+q*(s*x-tolerance)/(1+tolerance)
                exact.append(c)
            value=sum(exact)/len(exact);assert abs(result['blocks'][-1]['log_e_value']-math.log(float(value)))<1e-12;checked+=1
    invalid=0
    for bad in [[dict(block_id='x',score=2,mean_tolerance=0,support_radius=1)],[dict(block_id='x',score=0,mean_tolerance=0,support_radius=1)]*2]:
        try:evaluate(bad)
        except ValueError:invalid+=1
    assert invalid==2
    out=dict(status='PASS_APPLICATION_INTERFACES',planned_pulses=len(data),exact_path_checks=checked,invalid_contracts_rejected=invalid,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')})
    d=Path(__file__).resolve().parents[1]/'results';d.mkdir(exist_ok=True);(d/'APPLICATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
