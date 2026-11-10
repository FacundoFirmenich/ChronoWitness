"""Rational spectral projectors for declared triangular kinetic systems.

Time unit is arbitrary; interval length is log(2), integer rates are test inputs.
Integrals are represented as a + b log(2), never sampled biological observations.
"""
from fractions import Fraction as Q

def eye(n):return [[Q(i==j) for j in range(n)] for i in range(n)]
def zero(n):return [[Q(0) for _ in range(n)] for _ in range(n)]
def add(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scale(a,c):return [[x*c for x in r] for r in a]
def mul(a,b):return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def mv(a,x):return [sum(u*v for u,v in zip(r,x)) for r in a]
def spectral(m):
    n=len(m);ident=eye(n);lambdas=[m[i][i] for i in range(n)]
    assert len(set(lambdas))==n and all(m[i][j]==0 for i in range(n) for j in range(i+1,n))
    end=zero(n);i0=zero(n);ilog=zero(n);ps=[]
    for lam in lambdas:
        p=ident
        for other in lambdas:
            if other!=lam:p=mul(p,scale(add(m,scale(ident,-other)),1/(lam-other)))
        ps.append(p);b=Q(2)**int(lam);assert lam==int(lam)
        end=add(end,scale(p,b))
        if lam==0:ilog=add(ilog,p)
        else:i0=add(i0,scale(p,(b-1)/lam))
        assert mul(m,p)==scale(p,lam)
    assert sum_matrices(ps)==ident
    assert mul(m,end)==mul(end,m)
    assert mul(m,i0)==add(end,scale(ident,-1)) and mul(m,ilog)==zero(n)
    return end,i0,ilog
def sum_matrices(xs):
    out=zero(len(xs[0]))
    for x in xs:out=add(out,x)
    return out
def cycle(word,maps):
    n=len(maps[0][0]);p=eye(n);i0=zero(n);il=zero(n)
    for z in map(int,word):
        e,a,b=maps[z];i0=add(i0,mul(a,p));il=add(il,mul(b,p));p=mul(e,p)
    return p,i0,il
def periodic(p):
    x=[Q(1)]
    for i in range(1,len(p)):x.append(sum(p[i][j]*x[j] for j in range(i))/(1-p[i][i]))
    assert mv(p,x)==x
    return x
def window(cyc,x,k,r):
    p,a,b=cyc
    for _ in range(k):x=mv(p,x)
    start=x[:];s0=[Q(0)]*len(x);sl=s0[:]
    for _ in range(r):
        s0=[u+v for u,v in zip(s0,mv(a,x))];sl=[u+v for u,v in zip(sl,mv(b,x))];x=mv(p,x)
    return start,x,s0,sl
def model(kappa,eq,g,cascade):
    # x'=A x + b0,z + b1,z p. All synthesis intensities are nonnegative on [0,1].
    maps=[];matrices=[]
    for z in (0,1):
        s0=Q(1) if g[z]<0 else Q(0)
        if cascade:m=[[0,0,0,0],[kappa[z]*eq[z],-kappa[z],0,0],[s0,g[z],-4,0],[0,0,4,-5]]
        else:m=[[0,0,0],[kappa[z]*eq[z],-kappa[z],0],[s0,g[z],-4]]
        m=[[Q(x) for x in row] for row in m];matrices.append(m);maps.append(spectral(m))
    return matrices,maps
