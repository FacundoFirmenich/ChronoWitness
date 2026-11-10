"""Evaluate the supplied bounded-block e-process from explicitly qualified scores."""
import argparse,csv,json,math
from pathlib import Path
STAKES={'four':[1/8,1/4,1/2,1],'six':[1/32,1/16,1/8,1/4,1/2,1]}

def evaluate(rows,mixture='four',alpha=.05):
    if not 0<alpha<1:raise ValueError('alpha must be in (0,1)')
    stakes=STAKES[mixture];capital=[0.]*(2*len(stakes));seen=set();out=[];crossing=None
    for n,row in enumerate(rows,1):
        label=str(row['block_id'])
        if not label or label in seen:raise ValueError('block_id must be nonempty and unique')
        seen.add(label);x,t,r=(float(row[k]) for k in ['score','mean_tolerance','support_radius'])
        if not all(map(math.isfinite,[x,t,r])) or r<=0 or t<0 or abs(x)>r:raise ValueError('Invalid finite range or tolerance contract')
        for k,(sign,q) in enumerate((s,q) for s in [1,-1] for q in stakes):
            increment=q*(sign*x-t)/(r+t)
            capital[k]+=math.log1p(increment) if increment>-1 else -math.inf
        largest=max(capital)
        log_e=largest+math.log(sum(math.exp(v-largest) for v in capital)/len(capital)) if math.isfinite(largest) else -math.inf
        if crossing is None and log_e>=math.log(1/alpha):crossing=n
        out.append(dict(block=n,block_id=label,log_e_value=log_e if math.isfinite(log_e) else None,rejected_by_now=crossing is not None))
    if not out:raise ValueError('At least one block is required')
    return dict(status='COMPUTED_FROM_DECLARED_BLOCK_CONTRACT',alpha=alpha,mixture=mixture,first_crossing=crossing,blocks=out,interpretation='Validity requires qualified conditional mean/support bounds and predictable tolerances; the CSV alone does not establish these assumptions.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv',type=Path);p.add_argument('--mixture',choices=STAKES,default='four');p.add_argument('--alpha',type=float,default=.05);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    with a.csv.open(newline='') as f:result=evaluate(list(csv.DictReader(f)),a.mixture,a.alpha)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(dict(status=result['status'],blocks=len(result['blocks']),first_crossing=result['first_crossing']),indent=2))
if __name__=='__main__':main()
