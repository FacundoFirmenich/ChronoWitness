"""Algebraic two-state identity and bounded exact search for a 3-state witness."""
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
from audit_stochastic import WORDS

ROOT=Path(__file__).resolve().parents[1]

def numerator(word, current):
    # Coefficient of a_source*b0**n0*b1**n1 in D*sum_t[p_t*1(z_t=current)].
    terms=Counter()
    L=len(word)
    for t in range(L):
        if int(word[t]) != current:
            continue
        n0=n1=0
        for k in range(1,L+1):
            source=int(word[(t-k)%L])
            terms[(source,n0,n1)]+=1
            n0+=source==0
            n1+=source==1
    return terms

def mm(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b)))
             for j in range(len(b))] for i in range(len(a))]

def solve(a,b):
    n=len(b)
    a=[list(row)+[value] for row,value in zip(a,b)]
    for k in range(n):
        pivot=next((i for i in range(k,n) if a[i][k]),None)
        if pivot is None:
            raise ValueError('Singular system')
        a[k],a[pivot]=a[pivot],a[k]
        scale=a[k][k]
        a[k]=[v/scale for v in a[k]]
        for i in range(n):
            if i!=k:
                scale=a[i][k]
                a[i]=[x-scale*y for x,y in zip(a[i],a[k])]
    return [row[-1] for row in a]

def profile(word, matrices):
    n=len(matrices[0])
    block=[[F(i==j) for j in range(n)] for i in range(n)]
    for z in map(int,word):
        block=mm(block,matrices[z])
    a=[[block[j][i]-F(i==j) for j in range(n)] for i in range(n-1)]
    a.append([F(1)]*n)
    p=solve(a,[F(0)]*(n-1)+[F(1)])
    assert all(v>=0 for v in p) and mm([p],block)[0]==p
    initial=p[:]
    out=[F(0)]*(2*n)
    for z in map(int,word):
        for i,v in enumerate(p):
            out[2*i+z]+=v/len(word)
        p=mm([p],matrices[z])[0]
    assert p==initial
    return out

def main():
    identities=[]
    for z in (0,1):
        a,b=(numerator(w,z) for w in WORDS)
        assert a==b
        identities.append(dict(current_symbol=z, monomials=len(a),
           sum_coefficients=sum(a.values()), coefficients=[[*key,value] for key,value in sorted(a.items())]))
    witness=None
    for index,delta in enumerate(product(range(3),repeat=6)):
        # P_z = D_z/2 + J/6: every entry is >=1/6, hence unique periodic law.
        matrices=[[[F(1,6)+F(delta[2*i+z]==j,2) for j in range(3)]
                   for i in range(3)] for z in (0,1)]
        pa,pb=(profile(w,matrices) for w in WORDS)
        if pa!=pb:
            witness=dict(search_index=index, deterministic_table=list(delta),
                matrices=[[[str(v) for v in row] for row in mat] for mat in matrices],
                profile_A=list(map(str,pa)),profile_B=list(map(str,pb)),
                contrasts=list(map(str,[x-y for x,y in zip(pa,pb)])))
            break
    result=dict(two_state_polynomial_identities=identities,three_state_witness=witness,
                searched_candidates=index+1, biological_data=False,
                scope='Strictly positive input-conditioned Markov transition matrices; stationary state-symbol occupations')
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/MARKOV_BOUNDARY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='two_state_polynomial_identities'},indent=2))

if __name__=='__main__':
    main()
