"""Independent outward-rounded uniformization and Markov-tree verification.

This module imports no spectral construction or stationary linear solver.
All decisions use rational intervals on a fixed decimal grid.
"""
from fractions import Fraction as F
SCALE=10**50
def down(x):return F((x*SCALE).numerator//(x*SCALE).denominator,SCALE)
def up(x):return -down(-x)
def box(a,b=None):return down(F(a)),up(F(a if b is None else b))
def add(x,y):return down(x[0]+y[0]),up(x[1]+y[1])
def sub(x,y):return down(x[0]-y[1]),up(x[1]-y[0])
def mul(x,y):
    p=[a*b for a in x for b in y];return down(min(p)),up(max(p))
def div(x,y):
    assert y[0]>0
    return mul(x,(1/y[1],1/y[0]))
def summ(xs):
    v=box(0)
    for x in xs:v=add(v,x)
    return v
def eye():return [[box(i==j) for j in range(3)] for i in range(3)]
def zero():return [[box(0) for _ in range(3)] for _ in range(3)]
def matrix_add(a,b):return [[add(a[i][j],b[i][j]) for j in range(3)] for i in range(3)]
def matrix_scale(a,s):return [[mul(v,s) for v in r] for r in a]
def matrix_mul(a,b):return [[summ(mul(a[i][k],b[k][j]) for k in range(3)) for j in range(3)] for i in range(3)]
def row(v,a):return [summ(mul(v[i],a[i][j]) for i in range(3)) for j in range(3)]
def log2_bounds(n=256):
    lo=sum((F(1,k*2**k) for k in range(1,n+1)),F(0))
    return box(lo,lo+F(1,(n+1)*2**n))
def uniformize(p,duration,terms=128):
    assert duration in (1,2,4,8) and terms>0
    assert all(sum(r)==1 and min(r)>=0 for r in p)
    kernel=[[box(v) for v in r] for r in p];power=eye()
    h=mul(box(duration),log2_bounds());u=mul(box(2),h)
    probability=box(F(2)**(-2*duration));cdf=box(0)
    transition=zero();integral=zero();weight_sum=box(0)
    for n in range(terms):
        cdf=add(cdf,probability)
        weight=div(sub(box(1),cdf),box(2))
        weight=(max(F(0),weight[0]),max(F(0),weight[1]))
        transition=matrix_add(transition,matrix_scale(power,probability))
        integral=matrix_add(integral,matrix_scale(power,weight))
        weight_sum=add(weight_sum,weight)
        probability=div(mul(probability,u),box(n+1))
        power=matrix_mul(power,kernel)
    tail_p=max(F(0),1-cdf[0]);tail_j=max(F(0),h[1]-weight_sum[0])
    for i in range(3):
        for j in range(3):
            transition[i][j]=(max(F(0),transition[i][j][0]),min(F(1),up(transition[i][j][1]+tail_p)))
            integral[i][j]=(max(F(0),integral[i][j][0]),up(integral[i][j][1]+tail_j))
    return transition,integral,dict(poisson_tail_upper=str(tail_p),integrated_tail_upper=str(tail_j),terms=terms,decimal_places=50)
def stationary_tree(t):
    weights=[]
    for i in range(3):
        j,k=[x for x in range(3) if x!=i]
        weights.append(summ([mul(t[j][i],t[k][i]),mul(t[j][i],t[k][j]),mul(t[j][k],t[k][i])]))
    total=summ(weights);return [div(w,total) for w in weights]
def cycle(word,ops):
    total=eye()
    for z in map(int,word):total=matrix_mul(total,ops[z][0])
    p=stationary_tree(total);v=[[box(0) for _ in range(3)] for _ in range(2)]
    for z in map(int,word):
        s=row(p,ops[z][1]);v[z]=[add(x,y) for x,y in zip(v[z],s)]
        p=row(p,ops[z][0])
    return v
