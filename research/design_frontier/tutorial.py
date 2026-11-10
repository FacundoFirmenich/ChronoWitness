"""A short exact walkthrough from matched inputs to an observation/test contract."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,math,time
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'analysis'))
from verify_markov_boundary import forward
from audit_stochastic import periodic_profile
WORDS=('101111110010110010001000','100010110010111111001000')
def promoter_constant(word):
    b=[F(1,2),F(1,4)];r=[F(1,4),F(3,4)];rate=[F(1),F(2)];a=[r[z]*(1-b[z]) for z in range(2)]
    offset=F(0);rho=F(1)
    for z in map(int,word):offset=a[z]+b[z]*offset;rho*=b[z]
    p=offset/(1-rho);constant=F(0);logcoefficient=F(0)
    for z in map(int,word):
        constant+=(p-r[z])*(1-b[z])/rate[z];logcoefficient+=r[z];p=a[z]+b[z]*p
    return constant,logcoefficient

def main():
    start=time.perf_counter();assert forward(WORDS[0])==forward(WORDS[1])
    profiles=[periodic_profile(w,(F(1,8),F(5,8),F(9,16),F(13,16))) for w in WORDS];assert profiles[0]==profiles[1]
    integral=[promoter_constant(w) for w in WORDS];assert integral[0]==integral[1]
    # A common synthesis/degradation gain of 3/2 transports the mean equality.
    mean_constant=integral[0][0]/24;mean_log=integral[0][1]/24
    cert=R/'results/DESIGN_CERTIFICATE.json'
    if not cert.exists():cert=R/'supplement-v011/data/Data_S12_design_certificate.json'
    c=json.loads(cert.read_text());delta=F(c['absolute_contrast'][0]);assert delta>0
    # Ideal paired state indicators at independent uniform phases; X=Ia-Ib is in [-1,1].
    # This is a declared observation model, not a biological calibration.
    alpha=.05;beta=.2;tolerance=0.;radius=1.
    # Rational sufficient bound: exp(3689/1000)>40, exp(161/100)>5.
    for x,target in [(F(3689,1000),40),(F(161,100),5)]:
        term=total=F(1)
        for j in range(1,65):term*=x/j;total+=term
        assert total>target
    sa,sb=F(1921,1000),F(1269,1000)
    assert sa*sa>F(3689,1000) and sb*sb>F(161,100)
    bound=2*(sa+sb)**2/delta**2;n=-(-bound.numerator//bound.denominator)
    out=dict(status='PASS_EXACT_TUTORIAL',two_state_profile=list(map(str,profiles[0])),promoter_integral_constant=str(integral[0][0]),promoter_integral_log2=str(integral[0][1]),reporter_gain='3/2',reporter_null='exactly zero',kinetic_certified_contrast_lower=str(delta),ideal_readout='Independent paired state-zero indicators, each sampled at a uniform time in the periodic cycle',score_radius='1',mean_tolerance='0',fixed_horizon_design={'alpha':alpha,'target_power':1-beta,'sufficient_blocks_certified':n,'method':'Hoeffding sufficient bound with rational upper bounds on logarithms and square roots; conservative, not minimal'},biological_calibration=False,elapsed_seconds=time.perf_counter()-start)
    (R/'results').mkdir(exist_ok=True);(R/'results/DESIGN_TUTORIAL.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
