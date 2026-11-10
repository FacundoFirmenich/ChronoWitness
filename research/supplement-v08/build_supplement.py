"""Export full supplementary data and check independent normalization/transient identities."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from collections import Counter
import csv,json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'analysis'))
from verify_phase_python import block,steady
from audit_markov_boundary import numerator
from verify_markov_boundary import forward
OUT=Path(__file__).resolve().parent/'data';OUT.mkdir(exist_ok=True)
pair=json.loads((ROOT/'sources/FD7_CERTIFICATE_v0.7.0.json').read_text())['pair']
words=[pair['sequence_A'],pair['sequence_B']]
def read(name):return json.loads((ROOT/'results'/name).read_text())
def write(name,head,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(head);writer.writerows(rows)
def main():
    poly=read('MARKOV_BOUNDARY.json');rows=[]
    for z in (0,1):
        a,b=[numerator(w,z) for w in words];assert a==b
        assert forward(words[0])==forward(words[1])
        for key in sorted(a):rows.append([z,*key,a[key],b[key]])
    assert len(rows)==332
    write('Data_S1_polynomial_coefficients.csv',['current_symbol','source_symbol','exponent_b0','exponent_b1','coefficient_A','coefficient_B'],rows)
    structure=read('DESIGN_STRUCTURE.json');(OUT/'Data_S2_structure.json').write_text(json.dumps(structure,indent=2)+'\n')
    rows=[]
    for k in range(1,9):
        counts=[Counter(''.join(w[(t+j)%24] for j in range(k)) for t in range(24)) for w in words]
        for v in sorted(counts[0].keys()|counts[1].keys()):rows.append([k,v,counts[0][v],counts[1][v]])
    write('Data_S2_cyclic_word_counts.csv',['word_length','cyclic_word','count_A','count_B'],rows)
    ins=read('READER_INSTRUMENT_INDEPENDENT.json');rows=[]
    for record in ins['independent_witness_records']:
        for phase,(a,b) in enumerate(zip(record['phase_fractions_A'],record['phase_fractions_B'])):
            assert abs(F(a)-F(1,2))==F(1,6) and F(b)==F(1,2)
            rows.append([record['initial_joint_state'],phase,a,b,str(abs(F(a)-F(1,2))),str(abs(F(b)-F(1,2)))])
    write('Data_S3_instrument_phase_initial.csv',['initial_joint_state','phase','fraction_A','fraction_B','runwise_deviation_A','runwise_deviation_B'],rows)
    enum=read('PHASE_ENSEMBLE_CERTIFICATE.json');assert enum['stationary_profile_denominator']==288 and enum['phase_mean_from_sum_denominator']==6912
    keys=['states','transition_functions','initial_state_cases','fixed_phase0_separating_cases','common_phase_separating_cases','phase_mean_separating_cases','phase_profile_multiset_separating_cases']
    write('Data_S4_deterministic_enumeration.csv',keys,[[r[k] for k in keys] for r in enum['classes']])
    witness=enum['classes'][3]['first_phase_mean_witness'];norm=[]
    for wi,label in enumerate(['A','B']):
        w=tuple(map(int,words[wi]));profiles=[]
        for phase in range(24):profiles.append(steady(block(w[phase:]+w[:phase],witness['delta'],4),witness['q0'],4))
        raw=witness['sum_scaled_'+label];assert sum(raw)==6912
        expected=[sum(v[j] for v in profiles)/(24*24) for j in range(8)]
        got=[F(v,enum['phase_mean_from_sum_denominator']) for v in raw];assert got==expected and sum(got)==1
        assert sum(F(v,enum['stationary_profile_denominator']) for v in raw)==24
        norm.append({'schedule':label,'raw_sum_total':sum(raw),'phase_mean':list(map(str,got)),'wrong_denominator_rejected':True})
    mark=poly['three_state_witness'];write('Data_S4_markov_occupations.csv',['state','symbol','A','B','difference_A_minus_B'],[[i//2,i%2,mark['profile_A'][i],mark['profile_B'][i],mark['contrasts'][i]] for i in range(6)])
    checks=0;parameters=0
    for b0,b1,r0,r1 in product([F(1,4),F(1,2),F(3,4)],[F(1,4),F(1,2),F(3,4)],[F(1,4),F(3,4)],[F(1,4),F(3,4)]):
        bs=[b0,b1];aa=[r0*(1-b0),r1*(1-b1)];parameters+=1
        for word in words:
            w=list(map(int,word));offset=F(0);rho=F(1);C=[F(0),F(0)]
            for z in w:C[z]+=rho;offset=aa[z]+bs[z]*offset;rho*=bs[z]
            assert rho==b0**12*b1**12;pstar=offset/(1-rho)
            for initial,k,n in product([F(0),F(1)],[0,1,3],[1,2,5]):
                p=initial;ps=pstar;coeff=[F(0),F(0)]
                for period in range(k+n):
                    for z in w:
                        if period>=k:coeff[z]+=p-ps
                        p=aa[z]+bs[z]*p;ps=aa[z]+bs[z]*ps
                expected=[(initial-pstar)*rho**k*(1-rho**n)/(1-rho)*v for v in C]
                assert coeff==expected;checks+=1
    report={'status':'PASS_EXACT_SUPPLEMENT','coefficient_rows':332,'instrument_phase_initial_rows':96,
       'normalization_checks':norm,'finite_promoter_transient':{'rational_parameter_sets':parameters,'checks':checks,
       'comparison':'Direct affine recurrence vs coefficients of h0,h1 in the closed geometric integral',
       'parameter_domain':{'b0_b1':['1/4','1/2','3/4'],'r0_r1':['1/4','3/4'],'initial_p':[0,1],'discarded_periods':[0,1,3],'measured_periods':[1,2,5]},
       'biological_parameters_or_observations':False},'source_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'analysis/audit_phase_ensemble.cpp']}}
    (OUT/'Data_S5_supplement_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','coefficient_rows','instrument_phase_initial_rows','finite_promoter_transient']}))
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='SHA256SUMS'}
    (OUT/'SHA256SUMS').write_text(''.join(f'{h}  {name}\n' for name,h in hashes.items()))
if __name__=='__main__':main()
