"""Independent exact verification of the full 2x2 one-way instrument class.

No simulated biological data. All 4096 transition tables, 16384 initial cases,
and 24 phases are exhausted. Primary computations use integer attractor counts;
independent Fraction routines verify the explicit witness and finite contract.
"""
from pathlib import Path
from itertools import product
from collections import Counter
from fractions import Fraction
import json,time
from verify_phase_python import block,steady,finite
ROOT=Path(__file__).resolve().parents[1]
def blocks(word,delta):
 out=[]
 for initial in range(4):
  q=initial;counts=[0]*8
  for z in word:counts[2*q+z]+=1;q=delta[2*q+z]
  out.append((q,counts))
 return out
def profile_scaled(table,initial):
 seen={};path=[];q=initial
 while q not in seen:seen[q]=len(path);path.append(q);q=table[q][0]
 cycle=path[seen[q]:];scale=12//len(cycle)
 return tuple(sum(table[q][1][j] for q in cycle)*scale for j in range(8))
def main():
 start=time.monotonic();pair=json.loads((ROOT/'sources/FD7_CERTIFICATE_v0.7.0.json').read_text())['pair'];a=tuple(map(int,pair['sequence_A']));b=tuple(map(int,pair['sequence_B']))
 ra=[a[i:]+a[:i] for i in range(24)];rb=[b[i:]+b[:i] for i in range(24)]
 counts=dict(transition_tables=0,table_initial_pairs=0,phase_mean_full_profile_separators=0,phase_law_full_profile_separators=0,phase_mean_instrument_bit_separators=0,phase_law_instrument_bit_separators=0)
 first=None
 for f in product(range(2),repeat=4):
  for g in product(range(2),repeat=8):
   delta=tuple(2*f[2*(q//2)+z]+g[2*q+z] for q in range(4) for z in range(2));counts['transition_tables']+=1
   ap=[[] for _ in range(4)];bp=[[] for _ in range(4)]
   for wa,wb in zip(ra,rb):
    ta=blocks(wa,delta);tb=blocks(wb,delta)
    for q0 in range(4):ap[q0].append(profile_scaled(ta,q0));bp[q0].append(profile_scaled(tb,q0))
   for q0 in range(4):
    pa,pb=ap[q0],bp[q0];ma=tuple(map(sum,zip(*pa)));mb=tuple(map(sum,zip(*pb)));da=[sum(v[j] for j in (2,3,6,7)) for v in pa];db=[sum(v[j] for j in (2,3,6,7)) for v in pb]
    counts['table_initial_pairs']+=1;counts['phase_mean_full_profile_separators']+=ma!=mb;counts['phase_law_full_profile_separators']+=Counter(pa)!=Counter(pb);counts['phase_mean_instrument_bit_separators']+=sum(da)!=sum(db);counts['phase_law_instrument_bit_separators']+=Counter(da)!=Counter(db)
    if first is None and sum(da)!=sum(db):first={'delta':list(delta),'reader_delta':list(f),'instrument_delta_by_joint_state_input':list(g),'initial_joint_state':q0,'mean_scaled_sum_A':sum(da),'mean_scaled_sum_B':sum(db),'normalization_to_time_fraction':6912}
 cpp=json.loads((ROOT/'results/READER_INSTRUMENT_CERTIFICATE.json').read_text())
 assert all(counts[k]==cpp[k] for k in counts);assert first==cpp['first_instrument_mean_witness']
 # Fraction-based witness verification uses the earlier independent algorithms.
 delta=tuple(first['delta']);records=[]
 for q0 in range(4):
  values_a=[];values_b=[]
  for phase,(wa,wb) in enumerate(zip(ra,rb)):
   ta=block(wa,delta,4);tb=block(wb,delta,4);pa=steady(ta,q0,4);pb=steady(tb,q0,4)
   assert pa==finite(ta,q0,4,burn=3,measure=12);assert pb==finite(tb,q0,4,burn=3,measure=12)
   values_a.append(sum(pa[j] for j in (2,3,6,7))/24);values_b.append(sum(pb[j] for j in (2,3,6,7))/24)
  mean_a=sum(values_a)/24;mean_b=sum(values_b)/24
  records.append({'initial_joint_state':q0,'phase_fractions_A':list(map(str,values_a)),'phase_fractions_B':list(map(str,values_b)),'mean_A':str(mean_a),'mean_B':str(mean_b),'contrast_B_minus_A':str(mean_b-mean_a)})
 assert all(set(r['phase_fractions_A']) <= {'1/3','2/3'} and set(r['phase_fractions_B'])=={'1/2'} for r in records)
 assert records[0]['mean_A']=='17/36' and records[0]['mean_B']=='1/2' and records[0]['contrast_B_minus_A']=='1/36'
 # For every input, upstream c copies the current symbol, and d toggles on 00.
 assert all(delta[2*(2*c+d)+z]==2*z+(d^int(c==0 and z==0)) for c,d,z in product((0,1),repeat=3))
 out={'status':'PASS_EXACT_DESIGN_ONLY','scope':'Deterministic homogeneous one-way 2-state reader x 2-state instrument, common initial state and uniform phase','counts':counts,'first_witness':first,'independent_witness_records':records,'finite_acquisition_witness':{'burn_cycles':3,'measurement_cycles':12,'symbol_period':24,'checks_both_words_all_phases_initial_states':192},'phase_initial_robust_per_run_summary':{'readout':'abs(instrument_bit_fraction-1/2)','A':'1/6','B':'0','all_24_phases_and_4_initial_states':True,'pooling':'Compute this summary per run before combining phase/initial-state mixtures.'},'equations':{'reader':'c_next=z','instrument':'d_next=d XOR indicator(c=0 AND z=0)'},'elapsed_seconds':time.monotonic()-start,'biological_data':False,'comparison_with_FD7':'The upstream reader alone is within the original nonseparating lower class. The separating observable is the downstream instrument-bit occupation.'}
 (ROOT/'results/READER_INSTRUMENT_INDEPENDENT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'counts':counts,'initial0_means':[records[0]['mean_A'],records[0]['mean_B']],'contrast':records[0]['contrast_B_minus_A'],'seconds':out['elapsed_seconds']},indent=2))
if __name__=='__main__':main()
