"""Exact and independent certified audit of the kinetic FD7 witness."""
from pathlib import Path
from fractions import Fraction as F
import csv,hashlib,json
import exact as e
import independent as independent
R=Path(__file__).resolve().parents[1];O=R/'results';O.mkdir(exist_ok=True)
def decimal(x,upper=False,places=24):
    unit=10**places;v=x*unit
    n=-((-v.numerator)//v.denominator) if upper else v.numerator//v.denominator
    sign='-' if n<0 else '';n=abs(n)
    return f'{sign}{n//unit}.{n%unit:0{places}d}'
def main():
    rows=[];curves=[];certificates=[];profile_checks=operator_checks=independent_checks=negative=0
    for duration in range(1,9):
        ops=[e.operators(e.Q0,(0,-1,-3),duration),e.operators(e.Q1,(0,-1,-2),duration)]
        cycles=[e.cycle(w,ops) for w in e.WORDS]
        for wi,w in enumerate(e.WORDS):
            for phase in range(24):
                rotated=e.cycle(w[phase:]+w[:phase],ops)
                assert rotated['values']==cycles[wi]['values'];profile_checks+=1
        # Identical kernels remove all input-order dependence.
        controls=[e.cycle(w,[ops[0],ops[0]]) for w in e.WORDS]
        assert controls[0]['values']==controls[1]['values'];negative+=1
        for z in range(2):
            for state in range(3):
                a=cycles[0]['values'][z][0][state]-cycles[1]['values'][z][0][state]
                b=cycles[0]['values'][z][1][state]-cycles[1]['values'][z][1][state]
                lo,hi=e.mean_bounds(a,b,duration)
                rows.append([duration,z,state,str(a),str(b),decimal(lo),decimal(hi,True)])
        for state in range(3):
            a=sum(c['values'][z][0][state]*sign for c,sign in zip(cycles,[1,-1]) for z in range(2))
            b=sum(c['values'][z][1][state]*sign for c,sign in zip(cycles,[1,-1]) for z in range(2))
            assert b==0
            lo,hi=e.mean_bounds(a,b,duration)
            curves.append([duration,state,str(a),str(b),decimal(lo),decimal(hi,True)])
        if duration==1:
            assert F(curves[0][2])==F(164102929043225508,9552006408031348146265)>0
            certificate=dict(generators=[e.Q0,e.Q1],pulse_duration='log(2)',transitions=[x[0] for x in ops],integral_constant=[x[1] for x in ops],integral_log2=[x[2] for x in ops],cycles=cycles,integrated_state0_contrast=curves[0][2],normalized_state0_contrast=curves[0][4:6])
            # The sampled boundary observable differs from continuous-time occupation.
            sampled=[]
            for w,c in zip(e.WORDS,cycles):
                p=c['stationary'];v=F(0)
                for z in map(int,w):v+=p[0];p=e.row(p,ops[z][0])
                sampled.append(v)
            sampled_contrast=sampled[0]-sampled[1]
            c_lo,c_hi=e.mean_bounds(F(curves[0][2]),F(0))
            assert sampled_contrast/24<c_lo or sampled_contrast/24>c_hi;negative+=1
            certificate['sampled_state0_contrast_sum']=str(sampled_contrast)
            eta=[3*min(v for row in c['transition'] for v in row) for c in cycles]
            coefficient=12*e.log2_bounds()[1]*(1/eta[0]+1/eta[1]+1)
            epsilon=F(1,10**9);guarantee=c_lo-epsilon*coefficient
            assert guarantee>0
            certificate['rate_robustness']=dict(norm='max_row_sum_absolute',minorization=[str(v) for v in eta],lipschitz_upper=str(coefficient),epsilon=str(epsilon),contrast_lower=str(guarantee),display_lower=decimal(guarantee),sufficient_radius_lower=str(c_lo/coefficient))
        if duration in (1,2,4,8):
            independent_ops=[independent.uniformize(p,duration) for p in (e.P0,e.P1)]
            bounds=independent.log2_bounds()
            for z in range(2):
                transition,constant,logarithmic=ops[z]
                for i in range(3):
                    for j in range(3):
                        lo,hi=independent_ops[z][0][i][j];assert lo<=transition[i][j]<=hi
                        a,b=e.linear_bounds(constant[i][j],logarithmic[i][j],bounds)
                        lo,hi=independent_ops[z][1][i][j];assert lo<=a<=b<=hi
                        operator_checks+=2
            vals=[independent.cycle(w,independent_ops) for w in e.WORDS]
            for wi in range(2):
                for z in range(2):
                    for state in range(3):
                        a,b=e.linear_bounds(cycles[wi]['values'][z][0][state],cycles[wi]['values'][z][1][state],bounds)
                        lo,hi=vals[wi][z][state];assert lo<=a<=b<=hi
                        independent_checks+=1
            d=independent.sub(independent.summ(vals[0][z][0] for z in range(2)),independent.summ(vals[1][z][0] for z in range(2)))
            normalized=independent.div(d,independent.mul(independent.box(24*duration),bounds))
            if duration==1:assert normalized[0]>0
            certificates.append(dict(duration_log2=duration,integrated_contrast=[str(v) for v in d],normalized_contrast=[decimal(normalized[0]),decimal(normalized[1],True)],uniformization=[x[2] for x in independent_ops]))
    assert profile_checks==384 and operator_checks==144 and independent_checks==48 and negative==9
    perturbations=[];epsilon=F(1,10**9)
    for case,changes in enumerate([[(0,0,1,1)],[(1,1,0,-1)],[(0,0,1,1),(1,1,0,-1)],[(0,2,1,-1),(1,0,2,1)]]):
        ps=[[r[:] for r in p] for p in [e.P0,e.P1]]
        for z,i,j,sign in changes:
            ps[z][i][j]+=sign*epsilon/4;ps[z][i][i]-=sign*epsilon/4
        for p,original in zip(ps,[e.P0,e.P1]):
            assert max(sum(2*abs(v-u) for v,u in zip(r,s)) for r,s in zip(p,original))<=epsilon
        pert_ops=[independent.uniformize(p,1) for p in ps]
        vals=[independent.cycle(w,pert_ops) for w in e.WORDS]
        d=independent.sub(independent.summ(vals[0][z][0] for z in range(2)),independent.summ(vals[1][z][0] for z in range(2)))
        normalized=independent.div(d,independent.mul(independent.box(24),independent.log2_bounds()))
        lower=F(certificate['rate_robustness']['contrast_lower'])
        assert normalized[0]>=lower>0
        perturbations.append([case,str(epsilon),decimal(normalized[0]),decimal(normalized[1],True),decimal(lower)])
    for filename,header,data in [('KINETIC_OCCUPATIONS.csv',['duration_log2','symbol','state','integral_constant','integral_log2','mean_lower','mean_upper'],rows),('KINETIC_CURVES.csv',['duration_log2','state','integral_constant','integral_log2','mean_lower','mean_upper'],curves),('KINETIC_PERTURBATIONS.csv',['case','generator_norm_radius','mean_lower','mean_upper','uniform_lower_bound'],perturbations)]:
        with (O/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.writer(f);w.writerow(header);w.writerows(data)
    (O/'KINETIC_CERTIFICATE.json').write_text(json.dumps(certificate,default=str,indent=2)+'\n')
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    result=dict(status='PASS_CERTIFIED_CONTINUOUS_TIME_FD7_WITNESS',counts=dict(duration_cases=8,phase_profiles=profile_checks,operator_interval_checks=operator_checks,independent_integral_checks=independent_checks,adverse_controls=negative,perturbation_controls=len(perturbations)),strictly_positive_off_diagonal_rates=True,continuous_time_integrated_observable=True,normalized_state0_contrast=certificate['normalized_state0_contrast'],rate_robustness=certificate['rate_robustness'],independent_certificates=certificates,biological_observations=False,parameter_fitting=False,source_sha256={p.name:sha(p) for p in Path(__file__).parent.glob('*.py')},output_sha256={p.name:sha(p) for p in O.glob('KINETIC_*') if p.suffix in ['.json','.csv'] and p.name not in ['KINETIC_AUDIT.json','KINETIC_PROBE.json']})
    (O/'KINETIC_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','output_sha256','independent_certificates']},indent=2))
if __name__=='__main__':main()
