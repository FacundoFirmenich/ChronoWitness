"""Matched-dose and matched-run controls for design specificity."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import sys,json
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'analysis'))
from verify_markov_boundary import forward
from tutorial import promoter_constant,WORDS

def cyclic_counts(word,k):return Counter(''.join(word[(i+j)%len(word)] for j in range(k)) for i in range(len(word)))
def runs(word):
    start=next(i for i in range(len(word)) if word[i]!=word[i-1]);w=word[start:]+word[:start];out=[];last=w[0];n=0
    for z in w:
        if z!=last:out.append((last,n));last=z;n=0
        n+=1
    out.append((last,n));return sorted(out)

def main():
    a,b=WORDS
    control=''.join('1'*i+'0'*j for i,j in zip([6,2,1,1,1,1],[3,3,2,2,1,1]))
    cases=[]
    for name,v in [('FD7',b),('matched_runs_control',control)]:
        assert len(v)==24 and v.count('1')==12 and runs(v)==runs(a)
        ca,cb=promoter_constant(a),promoter_constant(v);assert ca[1]==cb[1]
        differences=[]
        for k in range(1,9):
            x,y=cyclic_counts(a,k),cyclic_counts(v,k);differences.append(sum(abs(x[t]-y[t]) for t in x.keys()|y.keys()))
        cases.append(dict(name=name,word_a=a,word_b=v,length=24,ones=12,cyclic_switches=sum(v[i]!=v[i-1] for i in range(24)),same_symbol_labelled_run_multiset=True,word_count_l1=differences,two_state_polynomial_identity=forward(a)==forward(v),promoter_integral_contrast_constant=str(ca[0]-cb[0]),promoter_integral_contrast_log2='0'))
    assert cases[0]['two_state_polynomial_identity'] and not cases[1]['two_state_polynomial_identity']
    assert F(cases[0]['promoter_integral_contrast_constant'])==0 and F(cases[1]['promoter_integral_contrast_constant'])!=0
    out=dict(status='PASS_MATCHED_RUN_DESIGN_CONTROL',cases=cases,scope='Two fixed design pairs; establishes specificity of the uniform null, not optimality over all designs')
    (R/'results/DESIGN_CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
