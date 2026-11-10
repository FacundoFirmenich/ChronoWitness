"""Exact rational exponential-polynomial arithmetic, no fitted parameters.

An expression is sum_{rate,degree} coefficient*t**degree*exp(-rate*t).
At integer multiples of log(2) with integer rates, exponentials are rational;
only log(2) needs a rigorous interval. Shared arithmetic is explicit in S14.
"""
from fractions import Fraction as F
from functools import lru_cache

class EP:
    def __init__(self,terms=None):
        self.terms={ (F(r),int(k)):F(c) for (r,k),c in (terms or {}).items() if c }
        if any(k<0 for r,k in self.terms):raise ValueError('Negative polynomial degree')
    @staticmethod
    def term(rate=0,degree=0,coefficient=1):return EP({(F(rate),degree):F(coefficient)})
    @staticmethod
    def lift(x):return x if isinstance(x,EP) else EP.term(coefficient=x)
    def __add__(self,other):
        other=EP.lift(other);out=self.terms.copy()
        for k,c in other.terms.items():out[k]=out.get(k,F(0))+c
        return EP(out)
    __radd__=__add__
    def __neg__(self):return EP({k:-v for k,v in self.terms.items()})
    def __sub__(self,other):return self+-EP.lift(other)
    def __rsub__(self,other):return EP.lift(other)+-self
    def __mul__(self,other):
        other=EP.lift(other);out={}
        for (r,k),a in self.terms.items():
            for (s,l),b in other.terms.items():
                key=(r+s,k+l);out[key]=out.get(key,F(0))+a*b
        return EP(out)
    __rmul__=__mul__
    def __truediv__(self,x):return self* (1/F(x))
    def __eq__(self,other):return self.terms==EP.lift(other).terms
    def derivative(self):
        out=EP()
        for (r,k),c in self.terms.items():
            out+=EP.term(r,k,-r*c)
            if k:out+=EP.term(r,k-1,k*c)
        return out
    def at_zero(self):return sum(c for (r,k),c in self.terms.items() if k==0)
    def integral(self):
        """Integral from 0 to t. Does not use the moment propagator."""
        result=EP()
        for (r,k),c in self.terms.items():
            if r==0:result+=EP.term(0,k+1,c/F(k+1));continue
            a=-c/r;poly=EP.term(r,k,a)
            for j in range(k-1,-1,-1):
                a=F(j+1)*a/r;poly+=EP.term(r,j,a)
            result+=poly-poly.at_zero()
        return result
    def log2_interval(self,k):
        k=F(k)
        if k<0:raise ValueError('Nonnegative time required')
        if k==0:v=self.at_zero();return v,v
        lo,hi=log2_interval();lo*=k;hi*=k
        low=high=F(0)
        for (r,n),c in self.terms.items():
            exponent=r*k
            if exponent.denominator!=1:raise ValueError('Integer rate*time/log(2) required')
            weight=F(2)**(-int(exponent))
            a,b=c*lo**n*weight,c*hi**n*weight
            low+=min(a,b);high+=max(a,b)
        return low,high
    def serial(self):return [[str(r),k,str(c)] for (r,k),c in sorted(self.terms.items())]

@lru_cache(None)
def log2_interval():
    n=80;x=F(1,3)
    lo=2*sum(x**(2*j+1)/F(2*j+1) for j in range(n))
    remainder=2*x**(2*n+1)/F(2*n+1)/(1-x*x)
    return lo,lo+remainder

def rounded_interval(interval,places=18):
    a,b=interval;s=10**places
    return F((a*s).__floor__(),s),F((b*s).__ceil__(),s)
