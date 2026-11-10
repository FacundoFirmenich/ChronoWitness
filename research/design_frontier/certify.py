"""Certify a selected rational generator pair without the search's matrix exponential."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,hashlib,csv
P=Path(__file__).parent;R=P.parent;sys.path.insert(0,str(R/'kinetic_reader'))
import independent as iv
WORDS=('101111110010110010001000','100010110010111111001000')
OFF=[(i,j) for i in range(3) for j in range(3) if i!=j]
def exp_negative(u,terms=160):
    assert 0<=u<=16
    term=F(1);total=term
    for k in range(1,terms+1):term*=u/k;total+=term
    nxt=term*u/(terms+1);tail=nxt/(1-u/(terms+2))
    return iv.box(1/(total+tail),1/total)

def uniformize(q,h=F(1),terms=192):
    rate=F(8);assert all(sum(r)==0 for r in q)
    assert all(F(1,64)<=q[i][j]<=4 for i,j in OFF)
    p=[[F(i==j)+q[i][j]/rate for j in range(3)] for i in range(3)];assert min(v for row in p for v in row)>=0
    kernel=[[iv.box(v) for v in row] for row in p];power=iv.eye();prob=exp_negative(rate*h);cdf=iv.box(0);weights=iv.box(0);transition=iv.zero();integral=iv.zero()
    for n in range(terms):
        cdf=iv.add(cdf,prob);weight=iv.div(iv.sub(iv.box(1),cdf),iv.box(rate));weight=(max(F(0),weight[0]),max(F(0),weight[1]))
        transition=iv.matrix_add(transition,iv.matrix_scale(power,prob));integral=iv.matrix_add(integral,iv.matrix_scale(power,weight));weights=iv.add(weights,weight)
        prob=iv.div(iv.mul(prob,iv.box(rate*h)),iv.box(n+1));power=iv.matrix_mul(power,kernel)
    tp=max(F(0),1-cdf[0]);tj=max(F(0),h-weights[0])
    for i in range(3):
        for j in range(3):
            transition[i][j]=(max(F(0),transition[i][j][0]),min(F(1),iv.up(transition[i][j][1]+tp)))
            integral[i][j]=(max(F(0),integral[i][j][0]),iv.up(integral[i][j][1]+tj))
    return transition,integral,dict(transition_tail=str(tp),integral_tail=str(tj))

def contrast(qs,h=F(1)):
    packed=[uniformize(q,h) for q in qs];ops=[v[:2] for v in packed];v=[iv.cycle(w,ops) for w in WORDS]
    means=[[iv.div(iv.summ(arm[z][j] for z in range(2)),iv.box(24*h)) for j in range(3)] for arm in v]
    diff=[iv.sub(means[0][j],means[1][j]) for j in range(3)]
    return diff,means,ops,[v[2] for v in packed]

def main():
    src=R/'results/DESIGN_SEARCH.json';search=json.loads(src.read_text());s=search['selected'];rates=[F(v,s['denominator']) for v in s['rates_numerators']];qs=[]
    for z in range(2):
        q=[[F(0) for j in range(3)] for i in range(3)]
        for (i,j),v in zip(OFF,rates[6*z:6*z+6]):q[i][j]=v
        for i in range(3):q[i][i]=-sum(q[i])
        qs.append(q)
    diff,means,ops,tails=contrast(qs);sign=1 if diff[0][0]>0 else -1;signed=iv.mul(diff[0],iv.box(sign));assert signed[0]>0
    for j in range(3):assert abs(float(sum(diff[j])/2)-s['quantized_contrast'][j])<1e-10
    phase_checks=0
    for arm,w in enumerate(WORDS):
        for phase in [1,7,23]:
            v=iv.cycle(w[phase:]+w[:phase],ops)
            for j in range(3):
                mean=iv.div(iv.summ(v[z][j] for z in range(2)),iv.box(24));assert max(mean[0],means[arm][j][0])<=min(mean[1],means[arm][j][1]);phase_checks+=1
    eta=[]
    for w in WORDS:
        b=iv.eye()
        for z in map(int,w):b=iv.matrix_mul(b,ops[z][0])
        eta.append(3*min(x[0] for row in b for x in row))
    lipschitz=12*(1/eta[0]+1/eta[1]+1);radius=signed[0]/(2*lipschitz)
    null,_,_,_=contrast([qs[0],qs[0]]);assert all(lo<=0<=hi for lo,hi in null)
    baseline=json.loads((R/'supplement-v010/data/Data_S11_kinetic_certificate.json').read_text());old=[F(v) for v in baseline['normalized_state0_contrast']]
    curves=list(csv.DictReader((R/'supplement-v010/data/Data_S11_kinetic_curves.csv').open()))
    old_best=max(max(abs(F(r['mean_lower'])),abs(F(r['mean_upper']))) for r in curves if r['duration_log2']=='1')
    out=dict(mean_occupations=[[[str(x) for x in v] for v in arm] for arm in means],gain_over_original_best_state_lower=str(signed[0]/old_best),status='PASS_CERTIFIED_DESIGN_FRONTIER',protocol_sha256=search['protocol_sha256'],search_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),generators=[[[str(v) for v in row] for row in q] for q in qs],duration='1',readout='state zero in [0,1]',contrast=[[str(x) for x in interval] for interval in diff],absolute_contrast=[str(x) for x in signed],gain_over_original_state0_lower=str(signed[0]/old[1]),minorization_lower=[str(x) for x in eta],rate_lipschitz_upper=str(lipschitz),half_margin_radius=str(radius),phase_coordinate_checks=phase_checks,common_generator_null_enclosed=True,uniformization_tails=tails,terms=192,decimal_places=50,global_optimality=False,biological_observations=False,source_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in P.glob('*.py')})
    (R/'results/DESIGN_CERTIFICATE.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],contrast=[float(x) for x in signed],gain_lower=float(signed[0]/old[1]),half_margin_radius=float(radius)),indent=2))
if __name__=='__main__':main()
