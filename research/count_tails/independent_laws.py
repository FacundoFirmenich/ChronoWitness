"""Independent compound-Poisson oracle. Imports no envelope implementation.

Negative exponentials use an alternating series and squaring. Stop-loss uses
the finite lower-tail identity, not the PGF/Markov bound being tested.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import comb, factorial

@lru_cache(None)
def negative_exp_interval(x):
    x=F(x)
    if x<0: raise ValueError('Nonnegative rate required')
    if x==0:return F(1),F(1)
    steps=0
    while x>1: x/=2;steps+=1
    total=term=F(1);lo=F(0);hi=F(1)
    for k in range(1,130):
        term *= -x/k;total+=term
        if k%2:lo=total
        else:hi=total
    for _ in range(steps):lo,hi=lo*lo,hi*hi
    return lo,hi

@lru_cache(None)
def compound_coefficients(mass,p,limit):
    """PGF exp(mass*(J(z)-1)) = exp(-mass)*sum a_n z**n."""
    mass,p=F(mass),F(p)
    a=[F(1)]
    for n in range(1,limit+1):
        a.append(sum((mass**k/F(factorial(k)))*comb(n-1,k-1)*(1-p)**k*p**(n-k) for k in range(1,n+1)))
    return tuple(a)

def recursive_coefficients(mass,p,limit):
    mass,p=F(mass),F(p);a=[F(1)]
    for n in range(1,limit+1):
        a.append(mass/n*sum(k*(1-p)*p**(k-1)*a[n-k] for k in range(1,n+1)))
    return tuple(a)

def compound_stoploss_interval(n0,mass,p,r):
    mass,p,r=F(mass),F(p),F(r)
    mean=n0+mass/(1-p)
    if r<=n0:return mean-r,mean-r
    z=r-n0;limit=z.__floor__()
    a=compound_coefficients(mass,p,limit)
    correction=sum((z-k)*v for k,v in enumerate(a))
    low,high=negative_exp_interval(mass)
    lo=max(F(0),mean-r+low*correction)
    hi=min(mean,mean-r+high*correction)
    scale=10**24
    return F((lo*scale).__floor__(),scale),F((hi*scale).__ceil__(),scale)
