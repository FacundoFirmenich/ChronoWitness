"""Independent Fraction-based verification of phase and finite-window claims.

Exhausts every labelled binary transition table with<=3states and every initial
state and24input rotations. Audits two4state witnesses separately. No cells,
random samples or fitted parameters are generated.
"""
from collections import Counter
from fractions import Fraction
from itertools import product
from pathlib import Path
import hashlib,json,time

ROOT=Path(__file__).resolve().parents[1]

def block(word,delta,m):
    result=[]
    for initial in range(m):
        q=initial;counts=[0]*(2*m)
        for bit in word:
            counts[2*q+bit]+=1;q=delta[2*q+bit]
        result.append((q,tuple(counts)))
    return result

def steady(table,initial,m):
    seen={};path=[];q=initial
    while q not in seen:
        seen[q]=len(path);path.append(q);q=table[q][0]
    cycle=path[seen[q]:]
    return tuple(Fraction(sum(table[q][1][j] for q in cycle),len(cycle)) for j in range(2*m))

def finite(table,initial,m,burn=2,measure=6):
    q=initial
    for _ in range(burn):q=table[q][0]
    values=[0]*(2*m)
    for _ in range(measure):
        for j in range(2*m):values[j]+=table[q][1][j]
        q=table[q][0]
    return tuple(Fraction(v,measure) for v in values)

def analyse_witness(a,b,delta):
    records=[]
    for q0 in range(4):
        ap=[];bp=[];maps_a=[];maps_b=[]
        for phase in range(24):
            wa=a[phase:]+a[:phase];wb=b[phase:]+b[:phase]
            ba=block(wa,delta,4);bb=block(wb,delta,4)
            pa=steady(ba,q0,4);pb=steady(bb,q0,4)
            ap.append(pa);bp.append(pb)
            maps_a.append([x[0] for x in ba]);maps_b.append([x[0] for x in bb])
        mean_a=tuple(sum(p[j] for p in ap)/24 for j in range(8))
        mean_b=tuple(sum(p[j] for p in bp)/24 for j in range(8))
        records.append({'q0':q0,'mean_A':list(map(str,mean_a)),'mean_B':list(map(str,mean_b)),
            'phase_mean_equal':mean_a==mean_b,'profile_law_equal':Counter(ap)==Counter(bp),
            'readout_state3_A':[str(sum(p[6:])/24) for p in ap],
            'readout_state3_B':[str(sum(p[6:])/24) for p in bp],
            'paired_phases_separating':sum(x!=y for x,y in zip(ap,bp)),
            'profiles_A':[list(map(str,p)) for p in ap],
            'profiles_B':[list(map(str,p)) for p in bp],
            'block_maps_A':maps_a,'block_maps_B':maps_b})
    return {'delta':list(delta),'records':records}

def main():
    started=time.monotonic()
    source=ROOT/'sources/FD7_CERTIFICATE_v0.7.0.json'
    original=json.loads(source.read_text());a=tuple(map(int,original['pair']['sequence_A']));b=tuple(map(int,original['pair']['sequence_B']))
    cpp=json.loads((ROOT/'results/PHASE_ENSEMBLE_CERTIFICATE.json').read_text())
    summaries=[];counterexample=None
    for m in (1,2,3):
        fixed=common=finite_checks=mean_diff=law_diff=cases=machines=0
        for delta in product(range(m),repeat=2*m):
            machines+=1
            aa=[[] for _ in range(m)];bb=[[] for _ in range(m)]
            for phase in range(24):
                ba=block(a[phase:]+a[:phase],delta,m);bt=block(b[phase:]+b[:phase],delta,m)
                for q0 in range(m):
                    pa=steady(ba,q0,m);pb=steady(bt,q0,m)
                    assert pa==finite(ba,q0,m) and pb==finite(bt,q0,m)
                    finite_checks+=2
                    if pa!=pb:
                        common+=1
                        if phase==0:fixed+=1
                        if counterexample is None:
                            counterexample={'states':m,'delta':list(delta),'q0':q0,'phase':phase,
                               'profile_A':list(map(str,pa)),'profile_B':list(map(str,pb))}
                    aa[q0].append(pa);bb[q0].append(pb)
            for q0 in range(m):
                cases+=1
                ma=tuple(sum(p[j] for p in aa[q0]) for j in range(2*m))
                mb=tuple(sum(p[j] for p in bb[q0]) for j in range(2*m))
                mean_diff+=ma!=mb;law_diff+=Counter(aa[q0])!=Counter(bb[q0])
        row={'states':m,'transition_functions':machines,'initial_state_cases':cases,
             'fixed_phase0_separating_cases':fixed,'common_phase_separating_cases':common,
             'phase_mean_separating_cases':mean_diff,'phase_profile_multiset_separating_cases':law_diff,
             'finite_window_checks_burn2_measure6':finite_checks}
        expected=cpp['classes'][m-1]
        assert all(row[k]==expected[k] for k in row),(row,expected)
        summaries.append(row)
    old=analyse_witness(a,b,(0,0,0,2,1,3,3,3))
    sync=analyse_witness(a,b,(0,1,0,2,1,3,2,1))
    assert all(r['phase_mean_equal'] and r['profile_law_equal'] for r in old['records'])
    expected_a=['3','3','3','5','4','3','2','1'];expected_b=['3','5','5','4','3','2','1','1']
    for r in sync['records']:
        assert all(p==expected_a for p in r['profiles_A'])
        assert all(p==expected_b for p in r['profiles_B'])
        assert all(len(set(row))==1 for row in r['block_maps_A']+r['block_maps_B'])
    out={'status':'PASS_EXACT_MATHEMATICAL_DESIGN_ONLY',
         'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'independent_lower_classes':summaries,'first_phase_specific_counterexample':counterexample,
         'absorbing_witness':old,'synchronizing_witness':sync,
         'lower_bound_phase_balanced_minimum_states':4,
         'phase_balanced_minimum_states_certified':4,
         'synchronizing_witness_profile_A':expected_a,'synchronizing_witness_profile_B':expected_b,
         'state3_fraction_A':'1/8','state3_fraction_B':'1/12','state3_contrast':'1/24',
         'finite_window':{'lower_class_max_states':3,'burn_cycles':2,'measure_cycles':6,
                          'symbols_per_cycle':24,'burn_symbols':48,'measure_symbols':144},
         'elapsed_seconds':time.monotonic()-started,
         'biological_data':False,'policy':'No backward promotion of earlier phase-specific certificates.'}
    (ROOT/'results/PHASE_INDEPENDENT_PYTHON.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'lower_class_initial_cases':sum(r['initial_state_cases'] for r in summaries),
                     'finite_window_checks':sum(r['finite_window_checks_burn2_measure6'] for r in summaries),
                     'phase_balanced_minimum_states':4,'independent_synchronizing_witness_profiles_verified':True,
                     'elapsed_seconds':out['elapsed_seconds']}))

if __name__=='__main__':main()
