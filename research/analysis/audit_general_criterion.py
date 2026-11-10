"""Structural audit of the general occupation criterion and biological boundary.

Mathematical words/matrices only. No physical calibration or biological samples.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
from audit_markov_boundary import numerator
from verify_markov_boundary import forward
from audit_stochastic import periodic_profile, WORDS

ROOT=Path(__file__).resolve().parents[1]

def backward_polynomial(w,z):
    out={}
    for (source,n0,n1),value in numerator(w,z).items():
        key=[0,0,n0,n1];key[source]=1
        out[tuple(key)]=value
    return out

def determinant3(m):
    return (m[0][0]*(m[1][1]*m[2][2]-m[1][2]*m[2][1])
           -m[0][1]*(m[1][0]*m[2][2]-m[1][2]*m[2][0])
           +m[0][2]*(m[1][0]*m[2][1]-m[1][1]*m[2][0]))

def main():
    checked=0
    for length in range(1,9):
        for bits in product('01',repeat=length):
            w=''.join(bits)
            expected=[backward_polynomial(w,z) for z in (0,1)]
            assert expected==forward(w)
            assert expected==forward(w[1:]+w[:1])
            checked+=1
    # Negative control: matched symbol counts alone do not imply the identity.
    a,b='0011','0101'
    assert forward(a)!=forward(b)
    witness=None
    for theta in product([F(1,4),F(1,2),F(3,4)],repeat=4):
        # Positive b_z: within the embeddable two-state kinetic domain.
        if not (theta[1]>theta[0] and theta[3]>theta[2]):continue
        pa,pb=periodic_profile(a,theta),periodic_profile(b,theta)
        if pa!=pb:
            witness=dict(words=[a,b],theta=list(map(str,theta)),
                         profile_A=list(map(str,pa)),profile_B=list(map(str,pb)))
            break
    assert witness is not None
    for w in WORDS:
        assert forward(w)==forward(WORDS[0])
    data=json.loads((ROOT/'results/MARKOV_BOUNDARY.json').read_text())
    matrices=[[[F(v) for v in row] for row in m] for m in data['three_state_witness']['matrices']]
    determinants=[determinant3(m) for m in matrices]
    assert determinants==[F(-1,4),F(0)]
    # exp(Q*d) always has determinant exp(d*tr(Q))>0 for a finite generator.
    result=dict(status='PASS_EXACT',words_checked=checked,
        forward_backward_and_rotation_checks=True,
        matched_counts_negative_control=witness,
        three_state_witness_determinants=list(map(str,determinants)),
        homogeneous_continuous_time_embedding='EXCLUDED_FOR_BOTH_MATRICES_BY_DETERMINANT',
        biological_bridge='Analytical two-state kinetic and linear-reporter mean theorem; no observed biological data',
        biological_data=False)
    (ROOT/'results/GENERAL_CRITERION.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
