"""Check forward polynomial recurrences and direct finite probability propagation.

Does not import the proposer, its polynomial builder, or its linear-system solver.
"""
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path
import copy
import json

ROOT=Path(__file__).resolve().parents[1]
A='101111110010110010001000'
B='100010110010111111001000'
ONE={(0,0,0,0):1}

def add(*polys):
    out=defaultdict(int)
    for p in polys:
        for k,v in p.items(): out[k]+=v
    return {k:v for k,v in out.items() if v}

def shift(p, variable, sign=1):
    out={}
    for k,v in p.items():
        key=list(k);key[variable]+=1;out[tuple(key)]=sign*v
    return out

def forward(word):
    offset={};multiplier=ONE
    for z in map(int,word):
        offset=add(shift(ONE,z),shift(offset,2+z))
        multiplier=shift(multiplier,2+z)
    denominator=add(ONE,{k:-v for k,v in multiplier.items()})
    initial=offset
    totals=[{},{}]
    for z in map(int,word):
        totals[z]=add(totals[z],offset)
        offset=add(shift(denominator,z),shift(offset,2+z))
    assert offset==initial
    return totals

def check_coefficients(data):
    left,right=forward(A),forward(B)
    assert left==right
    assert len(data['two_state_polynomial_identities'])==2
    assert {r['current_symbol'] for r in data['two_state_polynomial_identities']}=={0,1}
    for record in data['two_state_polynomial_identities']:
        z=record['current_symbol'];expected={}
        for source,n0,n1,value in record['coefficients']:
            key=[0,0,n0,n1];key[source]=1
            assert tuple(key) not in expected
            expected[tuple(key)]=value
        assert expected==left[z]
        assert record['monomials']==len(expected)
        assert record['sum_coefficients']==sum(expected.values())==288

def step(p,z,matrices):
    return [sum(p[i]*matrices[z][i][j] for i in range(3)) for j in range(3)]

def cycle(p,w,matrices):
    total=[Q(0)]*6
    for z in map(int,w):
        for i in range(3): total[2*i+z]+=p[i]/24
        p=step(p,z,matrices)
    return p,total

def check_witness(data):
    item=data['three_state_witness']
    matrices=[[[Q(v) for v in row] for row in m] for m in item['matrices']]
    assert all(sum(row)==1 and all(v>0 for v in row) for m in matrices for row in m)
    expected=[[Q(v) for v in item['profile_'+letter]] for letter in ('A','B')]
    checks=0
    for wi,word in enumerate((A,B)):
        for phase in range(24):
            w=word[phase:]+word[:phase]
            ends=[]
            for i in range(3):
                start=[Q(i==j) for j in range(3)]
                end,_=cycle(start,w,matrices)
                final,occupation=cycle(end,w,matrices)
                assert final==end
                assert occupation==expected[wi]
                ends.append(end);checks+=1
            assert len(set(map(tuple,ends)))==1
    contrasts=[x-y for x,y in zip(*expected)]
    assert list(map(str,contrasts))==item['contrasts']
    assert contrasts[0]+contrasts[1]==Q(5,131072)
    return checks

def main():
    data=json.loads((ROOT/'results/MARKOV_BOUNDARY.json').read_text())
    check_coefficients(data)
    checks=check_witness(data)
    corrupted=copy.deepcopy(data)
    corrupted['two_state_polynomial_identities'][0]['coefficients'][0][-1]+=1
    try: check_coefficients(corrupted)
    except AssertionError: pass
    else: raise AssertionError('Corrupt coefficient accepted')
    corrupted=copy.deepcopy(data)
    corrupted['three_state_witness']['profile_A'][0]='0'
    try: check_witness(corrupted)
    except AssertionError: pass
    else: raise AssertionError('Corrupt occupation accepted')
    corrupted=copy.deepcopy(data)
    corrupted['two_state_polynomial_identities'].pop()
    try: check_coefficients(corrupted)
    except AssertionError: pass
    else: raise AssertionError('Incomplete coefficient certificate accepted')
    result=dict(status='PASS_EXACT',polynomial_construction='forward recurrence independent of backward coefficient proposer',
                witness_construction='direct two-cycle propagation from each basis state; no stationary solver',
                phase_word_initial_cases=checks, state0_contrast='5/131072',
                block_rows_identical_all_phases=True, mutation_rejections=3,
                finite_contract='one wash-in cycle; next-cycle expected profile exact; empirical random profile not exact',
                biological_data=False,external_peer_review=False)
    (ROOT/'results/MARKOV_VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
