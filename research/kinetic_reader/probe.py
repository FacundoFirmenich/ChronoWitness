"""Evaluate one explicitly specified kinetic construction; no parameter fit."""
from pathlib import Path
import json
import exact as e
def main():
    ops=[e.operators(e.Q0,(0,-1,-3)),e.operators(e.Q1,(0,-1,-2))]
    ca,cb=[e.cycle(w,ops) for w in e.WORDS]
    differences=[]
    for state in range(3):
        a=sum(ca['values'][z][0][state]-cb['values'][z][0][state] for z in range(2))
        b=sum(ca['values'][z][1][state]-cb['values'][z][1][state] for z in range(2))
        lo,hi=e.mean_bounds(a,b)
        differences.append(dict(state=state,integral_constant=str(a),integral_log2=str(b),mean_lower=str(lo),mean_upper=str(hi),display_lower=float(lo),display_upper=float(hi),certified_nonzero=lo>0 or hi<0))
    result=dict(status='EVALUATED_FIXED_KINETIC_CONSTRUCTION',generators=[e.Q0,e.Q1],pulse_duration='log(2)',differences=differences)
    out=Path(__file__).resolve().parents[1]/'results';out.mkdir(exist_ok=True)
    (out/'KINETIC_PROBE.json').write_text(json.dumps(result,default=str,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='generators'},indent=2))
if __name__=='__main__':main()
