"""Exact finite-reporter audit on a declared mathematical parameter domain.

Two flow constructions, periodic and finite integrals, endpoint correction,
positive-cascade bounds (including resonance), inaccessible endpoint control.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import csv,hashlib,json
import exact_flow as f
import independent_flow as independent
R=Path(__file__).resolve().parents[1];OUT=R/'results';OUT.mkdir(exist_ok=True)
WORDS=['101111110010110010001000','100010110010111111001000']

def weight_certificate(a,w,gamma):
    assert all(v>0 for v in w) and gamma>0
    assert all(a[i][j]>=0 for i in range(len(a)) for j in range(len(a)) if i!=j)
    assert all(sum(w[i]*a[i][j] for i in range(len(a)))<=-gamma*w[j] for j in range(len(a)))

def f_integral(rate,k,r):return Q(2)**(-rate*24*k)*(1-Q(2)**(-rate*24*r))/rate
def psi_integral(gamma,kappa,k,r):
    if gamma!=kappa:return (f_integral(kappa,k,r)-f_integral(gamma,k,r))/(gamma-kappa),Q(0)
    a=Q(2)**(-gamma*24*k);b=Q(2)**(-gamma*24*(k+r))
    return (a-b)/gamma**2,Q(24)*(k*a-(k+r)*b)/gamma

def main():
    rows=[];flow_checks=periodic_checks=windows=bounds=resonance=0;wrong_sign=hidden=0
    for case,(kap,eq,gs,cascade) in enumerate(product([(1,2),(2,1),(1,3),(3,2)],[(Q(1,4),Q(3,4)),(Q(3,4),Q(1,4))],[(Q(1),Q(2)),(Q(1),Q(-1))],[False,True])):
        matrices,maps=f.model(kap,eq,gs,cascade);n=len(matrices[0]);gamma=Q(2 if cascade else 4);w=[Q(2),Q(1)] if cascade else [Q(1)]
        a=[row[2:] for row in matrices[0][2:]];weight_certificate(a,w,gamma)
        ell=[-Q(1,5),-Q(1,5)] if cascade else [-Q(1,4)]
        assert [sum(ell[i]*a[i][j] for i in range(len(a))) for j in range(len(a))]==[Q(j==len(a)-1) for j in range(len(a))]
        # Independently reconstruct every column of each full-period operator.
        for phase in [0,1,7]:
            pairs=[]
            for wi,base in enumerate(WORDS):
                word=base[phase:]+base[:phase];cyc=f.cycle(word,maps);p,i0,il=cyc
                for j in range(n):
                    v=[Q(t==j) for t in range(n)];end,a0,al=independent.cycle(word,matrices,v)
                    assert end==f.mv(p,v) and a0==f.mv(i0,v) and al==f.mv(il,v);flow_checks+=1
                star=f.periodic(p);per0=f.mv(i0,star);perl=f.mv(il,star);pairs.append((per0,perl));periodic_checks+=1
                # J_g = integral g_z exp(-K(s)); exact rational at Delta=log(2).
                prefix=Q(1);jg=Q(0)
                for z in map(int,word):
                    b=Q(2)**(-kap[z]);jg+=prefix*gs[z]*(1-b)/kap[z];prefix*=b
                rho=prefix
                for pinit,reporter_init,k,r in product([0,1],[0,1],[0,1,3],[1,2,5]):
                    initial=[Q(1),Q(pinit)]+[Q(reporter_init)]*(n-2)
                    start,end,v0,vl=f.window(cyc,initial,k,r)
                    dx=[end[j]-start[j] for j in range(2,n)]
                    raw0=v0[-1]-r*per0[-1];rawl=vl[-1]-r*perl[-1]
                    correction=sum(u*v for u,v in zip(ell,dx))
                    corrected0=raw0-correction;ep=initial[1]-star[1]
                    expected=-ell[0]*ep*jg*rho**k*(1-rho**r)/(1-rho)
                    assert corrected0==expected and rawl==0;windows+=1
                    if correction and raw0+correction!=expected:wrong_sign+=1
                    if cascade and dx[0] and raw0-ell[-1]*dx[-1]!=expected:hidden+=1
                    ex=sum(w[j]*abs(initial[j+2]-star[j+2]) for j in range(n-2));g=max(abs(x)*w[0] for x in gs)
                    b0,bl=psi_integral(gamma,Q(min(kap)),k,r)
                    b0=ex*f_integral(gamma,k,r)+g*abs(ep)*b0;bl*=g*abs(ep)
                    assert independent.nonnegative(b0-raw0,bl-rawl) and independent.nonnegative(b0+raw0,bl+rawl)
                    bounds+=1;resonance+=int(gamma==min(kap))
                    # Window means are these integrals divided by 24*r*log(2).
                    rows.append([case,'maturation' if cascade else 'single',wi,phase,pinit,reporter_init,k,r,str(raw0),str(corrected0),str(expected),str(b0),str(bl)])
            assert pairs[0]==pairs[1],'FD7 periodic integrated state means differ'
    assert wrong_sign and hidden and resonance
    rejected=0
    for a,w,g in [([[Q(-1),Q(8)],[Q(0),Q(-1)]],[Q(1),Q(1)],Q(1)),([[Q(-1),Q(-1)],[Q(0),Q(-1)]],[Q(1),Q(1)],Q(1))]:
        try:weight_certificate(a,w,g)
        except AssertionError:rejected+=1
        else:raise AssertionError('Invalid positive contraction certificate accepted')
    # Resonant ODE q'=-q+e^-t has q=t e^-t: derivative and integral
    # are checked symbolically by rational polynomial coefficients.
    poly=[Q(0),Q(1)];der=[poly[1],Q(0)];forcing=[Q(1),Q(0)]
    assert [der[i]-poly[i] for i in range(2)]==[forcing[i]-poly[i] for i in range(2)]
    assert independent.nonnegative(Q(1,2),-Q(1,2)) # integral_0^log2 t e^-t = (1-log2)/2
    csvpath=OUT/'FINITE_REPORTER_WINDOWS.csv'
    with csvpath.open('w',newline='',encoding='utf-8') as out:
        writer=csv.writer(out);writer.writerow(['case','model','schedule','phase','initial_promoter','initial_reporter_each_stage','discarded_periods','measured_periods','raw_bias_integral','corrected_bias_integral','predicted_corrected_integral','bound_constant','bound_log2_coefficient']);writer.writerows(rows)
    result=dict(status='PASS_EXACT_FINITE_REPORTER',model_cases=32,flow_operator_columns=flow_checks,periodic_profiles=periodic_checks,finite_windows=windows,certified_raw_bounds=bounds,resonant_bound_cases=resonance,wrong_sign_controls=wrong_sign,hidden_endpoint_controls=hidden,rejected_invalid_weight_certificates=rejected,
      parameter_domain=dict(kappa_pairs=[[1,2],[2,1],[1,3],[3,2]],equilibria=[['1/4','3/4'],['3/4','1/4']],synthesis_contrasts=[[1,2],[1,-1]],single_decay=4,maturation_rate=4,mature_decay=5,interval='log(2) in arbitrary units',phases=[0,1,7],discard=[0,1,3],measure=[1,2,5]),
      independence='Rational spectral projectors vs componentwise ODE exponential coefficients; independent method imports no projector or matrix solver.',
      logarithm_bound='64 positive terms of 2*atanh(1/3), plus a rational upper bound on the remainder; no floating point in certification.',
      readout_boundary='C A^-1 must lie in the row span of endpoint measurement R for a universal exact correction from R*x endpoints.',
      empirical_data=False,source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))},csv_sha256=hashlib.sha256(csvpath.read_bytes()).hexdigest())
    (OUT/'FINITE_REPORTER.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','parameter_domain']},indent=2))
if __name__=='__main__':main()
