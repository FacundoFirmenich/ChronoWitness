"""Exact acquisition kernels at integer multiples of log(2).

Every returned pair is a + b log(2). Rates are positive integers in this
verification domain; the accompanying proofs are not restricted to that domain.
"""
from fractions import Fraction as Q

def add(a,b):return a[0]+b[0],a[1]+b[1]
def scale(a,c):return a[0]*c,a[1]*c
def sub(a,b):return add(a,scale(b,-1))
ZERO=(Q(0),Q(0))

def primitive(rate,n):
    """Integral twice of exp(-rate*t), causal at zero."""
    if n<=0:return ZERO
    e=Q(2)**(-rate*n)
    return -(1-e)/rate**2,Q(n)/rate

def cascade_primitive(gamma,kappa,n):
    if n<=0:return ZERO
    if gamma!=kappa:return scale(sub(primitive(kappa,n),primitive(gamma,n)),1/(gamma-kappa))
    e=Q(2)**(-gamma*n)
    return -2*(1-e)/gamma**3,Q(n)*(1+e)/gamma**2

def rectangle(rate,t0,t1,a,b,other=None):
    fun=(lambda n:primitive(rate,n)) if other is None else (lambda n:cascade_primitive(rate,other,n))
    return add(sub(fun(t1-a),fun(t0-a)),sub(fun(t0-b),fun(t1-b)))

def initial(rate,t0,t1):return ((Q(2)**(-rate*t0)-Q(2)**(-rate*t1))/rate,Q(0))
def initial_cascade(gamma,kappa,t0,t1):
    if gamma!=kappa:return scale(sub(initial(kappa,t0,t1),initial(gamma,t0,t1)),1/(gamma-kappa))
    a=Q(2)**(-gamma*t0);b=Q(2)**(-gamma*t1)
    return (a-b)/gamma**2,(t0*a-t1*b)/gamma

def weighted(values,rate,t0,t1,other=None):
    out=ZERO
    for j,d in enumerate(values[:t1]):
        if d:out=add(out,scale(rectangle(rate,t0,t1,j,j+1,other),d))
    return out
