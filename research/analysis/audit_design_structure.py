"""Direct structural checks of FD7, independent of archived summary fields."""
from collections import Counter
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def words(w,k):
 return Counter(''.join(w[(i+j)%len(w)] for j in range(k)) for i in range(len(w)))
def runs(w):
 # Start at a boundary so no cyclic run is split.
 i=next(i for i in range(len(w)) if w[i]!=w[i-1]);v=w[i:]+w[:i];out=[];start=0
 for j in range(1,len(v)+1):
  if j==len(v) or v[j]!=v[start]:out.append((v[start],j-start));start=j
 return sorted(out)
def auto(w):
 v=[2*int(x)-1 for x in w]
 return [sum(v[i]*v[(i+k)%len(w)] for i in range(len(w))) for k in range(len(w))]
def main():
 source=ROOT/'sources/FD7_CERTIFICATE_v0.7.0.json';old=json.loads(source.read_text());a=old['pair']['sequence_A'];b=old['pair']['sequence_B']
 assert len(a)==len(b)==24 and Counter(a)==Counter(b)=={'0':12,'1':12}
 diffs=[sum(abs(words(a,k)[w]-words(b,k)[w]) for w in words(a,k).keys()|words(b,k).keys()) for k in range(1,9)]
 assert diffs[:7]==[0]*7 and diffs[7]>0 and runs(a)==runs(b) and auto(a)==auto(b)
 orbit=set()
 for flip in (False,True):
  for reverse in (False,True):
   w=a[::-1] if reverse else a
   if flip:w=''.join('1' if s=='0' else '0' for s in w)
   for k in range(24):orbit.add(w[k:]+w[:k])
 assert b not in orbit
 out={'status':'PASS_EXACT_DESIGN_ONLY','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'sequence_A':a,'sequence_B':b,'cyclic_word_count_l1_differences_k1_to_k8':diffs,
 'cyclic_run_multiset_A':runs(a),'cyclic_run_multiset_B':runs(b),'autocorrelation_pm1_A':auto(a),'autocorrelation_pm1_B':auto(b),
 'B_outside_rotation_reflection_complement_orbit_of_A':True,'biological_data':False}
 (ROOT/'results/DESIGN_STRUCTURE.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
