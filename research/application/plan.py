"""Export an FD7 paired-block stimulation plan; this does not operate hardware."""
import argparse,csv,hashlib,json,random
from pathlib import Path
WORDS=('101111110010110010001000','100010110010111111001000')

def rows(blocks,pulse,periods,burn_in,seed):
    assert blocks>0 and pulse>0 and periods>0 and burn_in>=0
    rng=random.Random(seed)
    for block in range(1,blocks+1):
        assignment=rng.randrange(2);phase=rng.randrange(24)
        for unit in range(2):
            arm=unit^assignment;word=WORDS[arm][phase:]+WORDS[arm][:phase]
            for k in range(24*(burn_in+periods)):
                yield dict(block=block,unit_label=f'block{block}_unit{unit}',schedule='ab'[arm],phase=phase,pulse_index=k,start=k*pulse,end=(k+1)*pulse,input=int(word[k%24]),stage='wash_in' if k<24*burn_in else 'acquisition')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--blocks',type=int,required=True);p.add_argument('--pulse-duration',type=float,required=True);p.add_argument('--unit',required=True);p.add_argument('--periods',type=int,required=True);p.add_argument('--burn-in-periods',type=int,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    import math
    if not math.isfinite(a.pulse_duration) or a.pulse_duration<=0 or a.blocks<=0 or a.periods<=0 or a.burn_in_periods<0:p.error('Use finite positive durations, blocks and acquisition periods, and nonnegative wash-in periods.')
    data=list(rows(a.blocks,a.pulse_duration,a.periods,a.burn_in_periods,a.seed));a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    meta=dict(kind='stimulation_plan_not_observations',time_unit=a.unit,blocks=a.blocks,periods=a.periods,burn_in_periods=a.burn_in_periods,seed=a.seed,randomization='Independent random within-pair assignment and common uniform cyclic phase per block',delivery='Abstract binary command; hardware response, wash-in adequacy and time units require assay qualification',sha256=hashlib.sha256(a.out.read_bytes()).hexdigest())
    a.out.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
