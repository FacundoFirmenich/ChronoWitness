"""Exact reporter-rate/endpoint budgets and an adversarial two-state control."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import json,csv,hashlib
P=Path(__file__).resolve().parent;R=P.parent;O=R/'results';O.mkdir(exist_ok=True)

def main():
    protocol=json.loads((P/'PROTOCOL.json').read_text());cert=json.loads((R/'supplement-v011/data/Data_S12_design_certificate.json').read_text());delta=F(cert['absolute_contrast'][0]);rows=[];checks=0
    for g,h,eta,e in product(map(F,protocol['reporter_rates']),[24*k for k in protocol['windows_periods']],map(F,protocol['calibration_relative_rate_errors']),map(F,protocol['endpoint_absolute_errors'])):
        lo,hi=g*(1-eta),g*(1+eta);c=(1/lo+1/hi)/2;radius=(1/lo-1/hi)/2
        bias=2*radius/h+4*c*e/h;support=1+bias;gap=delta-2*bias
        # Independent extreme-value checks over reciprocal-rate and endpoint boxes.
        for actual,change,error in product([lo,hi],[-1,1],[-2*e,2*e]):
            residual=(c-1/actual)*change/h+c*error/h
            assert abs(residual)<=bias/2;checks+=1
        n=None
        if gap>0:
            bound=2*support**2*(F(1921,1000)+F(1269,1000))**2/gap**2;n=-(-bound.numerator//bound.denominator)
        rows.append(dict(gamma=str(g),periods=h//24,relative_rate_error=str(eta),endpoint_error=str(e),correction_coefficient=str(c),bias_allowance=str(bias),score_radius=str(support),guaranteed_gap=str(gap),status='POSITIVE_WORST_CASE_GAP' if gap>0 else 'NO_POSITIVE_WORST_CASE_GAP',sufficient_blocks=n))
    # General two-stage functional: known-point coefficients versus interval bounds.
    # a_M=kappa/(gamma*delta), a_P=1/delta. Box extrema follow monotonicity.
    two_stage=[]
    for spread in [F(1,100),F(1,10),F(1,4)]:
        gl,gu=1-spread,1+spread;kl,ku=2*(1-spread),2*(1+spread);dl,du=1-spread,1+spread
        intervals=[(kl/(gu*du),ku/(gl*dl)),(1/du,1/dl)];centers=[sum(x)/2 for x in intervals];radii=[(b-a)/2 for a,b in intervals]
        for g,k,d,dm,dp in product([gl,gu],[kl,ku],[dl,du],[-3,3],[-5,5]):
            error=(centers[0]-k/(g*d))*dm+(centers[1]-1/d)*dp
            assert abs(error)<=3*radii[0]+5*radii[1];checks+=1
        two_stage.append(dict(relative_box=str(spread),coefficient_intervals=[[str(v) for v in x] for x in intervals],endpoint_caps=['3','5'],single_arm_numerator_bound=str(3*radii[0]+5*radii[1])))
    with (O/'ASSAY_CALIBRATION.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    out=dict(status='PASS_EXACT_CALIBRATION_BUDGETS',rows=len(rows),extreme_checks=checks,positive_gap_cases=sum(r['status']=='POSITIVE_WORST_CASE_GAP' for r in rows),gap_definition='Certified latent contrast minus twice the worst-case observation bias',support_definition='1 plus the same total observation bias',endpoint_contract='Uniform endpoint bounds established before each block; observed post-block discrepancies alone are not predictable allowances',two_stage=two_stage,csv_sha256=hashlib.sha256((O/'ASSAY_CALIBRATION.csv').read_bytes()).hexdigest())
    (O/'ASSAY_CALIBRATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
