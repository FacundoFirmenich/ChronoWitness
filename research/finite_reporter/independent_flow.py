"""Independent componentwise ODE solution; no projector or matrix-solver imports."""
from fractions import Fraction as F

def step(matrix,initial):
    # Every component is a linear combination of exponentials with distinct rates.
    n=len(initial);solutions=[];end=[];integral0=[];integral_log=[]
    for i in range(n):
        lam=matrix[i][i];forcing={}
        for j in range(i):
            for rate,c in solutions[j].items():forcing[rate]=forcing.get(rate,F(0))+matrix[i][j]*c
        coeff={lam:initial[i]}
        for rate,c in forcing.items():
            if not c:continue
            assert rate!=lam
            coeff[rate]=coeff.get(rate,F(0))+c/(rate-lam)
            coeff[lam]-=c/(rate-lam)
        coeff={r:c for r,c in coeff.items() if c}
        assert sum(coeff.values())==initial[i]
        for rate in set(coeff)|set(forcing):assert (rate-lam)*coeff.get(rate,F(0))==forcing.get(rate,F(0))
        solutions.append(coeff)
        end.append(sum(c*F(2)**int(r) for r,c in coeff.items()))
        integral0.append(sum(c*(F(2)**int(r)-1)/r for r,c in coeff.items() if r))
        integral_log.append(coeff.get(F(0),F(0)))
    return end,integral0,integral_log

def cycle(word,matrices,initial):
    x=initial[:];a=[F(0)]*len(x);b=a[:]
    for z in map(int,word):
        x,c,d=step(matrices[z],x);a=[v+w for v,w in zip(a,c)];b=[v+w for v,w in zip(b,d)]
    return x,a,b

def log_two_interval(n=64):
    x=F(1,3);s=2*sum(x**(2*j+1)/F(2*j+1) for j in range(n))
    tail=2*x**(2*n+1)/(F(2*n+1)*(1-x*x))
    return s,s+tail

def nonnegative(a,b):
    lo,hi=log_two_interval()
    return a+b*(lo if b>=0 else hi)>=0
