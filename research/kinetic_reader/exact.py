"""Rational spectral construction of a continuous-time FD7 reader.

Rows are distributions. Durations are integer multiples of log(2).
Integrals are represented as rational constant + rational * log(2).
"""
from fractions import Fraction as F
N=3
WORDS=('101111110010110010001000','100010110010111111001000')
P0=[[F(v,6) for v in row] for row in [[4,1,1],[1,1,4],[1,4,1]]]
P1=[[F(v,6) for v in row] for row in [[4,1,1],[4,1,1],[1,1,4]]]
def eye():return [[F(i==j) for j in range(N)] for i in range(N)]
def zero():return [[F(0) for _ in range(N)] for _ in range(N)]
def add(a,b):return [[a[i][j]+b[i][j] for j in range(N)] for i in range(N)]
def scale(a,s):return [[v*s for v in row] for row in a]
def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(N)) for j in range(N)] for i in range(N)]
def row(v,a):return [sum(v[i]*a[i][j] for i in range(N)) for j in range(N)]
def gen(p):return scale(add(p,scale(eye(),-1)),2)
Q0,Q1=gen(P0),gen(P1)
def operators(q,eigenvalues,duration=1):
    assert isinstance(duration,int) and duration>0
    assert all(sum(r)==0 for r in q)
    assert all(q[i][j]>0 for i in range(N) for j in range(N) if i!=j)
    projectors={}
    for lam in eigenvalues:
        p=eye()
        for mu in eigenvalues:
            if mu!=lam:p=scale(mul(p,add(q,scale(eye(),-mu))),F(1,lam-mu))
        projectors[lam]=p
    total=zero()
    for lam,p in projectors.items():
        assert mul(q,p)==scale(p,lam)
        for mu,r in projectors.items():assert mul(p,r)==(p if lam==mu else zero())
        total=add(total,p)
    assert total==eye()
    transition=zero();constant=zero();logarithmic=scale(projectors[0],duration)
    for lam,p in projectors.items():
        transition=add(transition,scale(p,F(2)**(duration*lam)))
        if lam:constant=add(constant,scale(p,(F(2)**(duration*lam)-1)/lam))
    assert all(sum(r)==1 for r in transition) and all(x>0 for r in transition for x in r)
    assert mul(q,constant)==add(transition,scale(eye(),-1)) and mul(q,logarithmic)==zero()
    assert all(sum(r)==0 for r in constant) and all(sum(r)==duration for r in logarithmic)
    return transition,constant,logarithmic
def solve(a,b):
    a=[list(r)+[v] for r,v in zip(a,b)];n=len(a)
    for j in range(n):
        pivot=next(i for i in range(j,n) if a[i][j]);a[j],a[pivot]=a[pivot],a[j]
        d=a[j][j];a[j]=[x/d for x in a[j]]
        for i in range(n):
            if i!=j:
                d=a[i][j];a[i]=[x-d*y for x,y in zip(a[i],a[j])]
    return [r[-1] for r in a]
def stationary(t):
    a=[[t[i][j]-F(i==j) for i in range(N)] for j in range(N-1)]+[[F(1)]*N]
    p=solve(a,[F(0),F(0),F(1)])
    assert row(p,t)==p and sum(p)==1 and min(p)>0
    return p
def cycle(word,ops):
    t=eye();integrals=[[zero(),zero()] for _ in range(2)]
    for z in map(int,word):
        step,a,b=ops[z]
        integrals[z][0]=add(integrals[z][0],mul(t,a))
        integrals[z][1]=add(integrals[z][1],mul(t,b))
        t=mul(t,step)
    p=stationary(t)
    values=[[row(p,mat) for mat in pair] for pair in integrals]
    return dict(transition=t,stationary=p,integrals=integrals,values=values)
def log2_bounds(n=90):
    lo=sum((F(2,(2*j+1)*3**(2*j+1)) for j in range(n)),F(0))
    hi=lo+F(2,((2*n+1)*3**(2*n+1)))/(1-F(1,9))
    return lo,hi
def linear_bounds(a,b,log_bounds):
    lo,hi=log_bounds
    return (a+b*lo,a+b*hi) if b>=0 else (a+b*hi,a+b*lo)
def mean_bounds(a,b,duration=1):
    lo,hi=log2_bounds();v0,v1=linear_bounds(a,b,(lo,hi))
    return min(v0/(24*duration*lo),v0/(24*duration*hi),v1/(24*duration*lo),v1/(24*duration*hi)),max(v0/(24*duration*lo),v0/(24*duration*hi),v1/(24*duration*lo),v1/(24*duration*hi))
