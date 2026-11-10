"""Independent molecule-survival/Poisson-immigration derivation (SI S14).

Shares only rational expression arithmetic, never imports the ODE propagator.
"""
from fractions import Fraction as F
from exp_polynomial import EP

def moments(m0,p0,lam,kappa,gamma,delta):
    lam,k,g,d=map(F,(lam,kappa,gamma,delta))
    if min(g,d)<=0:raise ValueError('Positive degradation rates required')
    eg=EP.term(g);ed=EP.term(d)
    h=k*EP.term(d,1) if g==d else k*(ed-eg)/(g-d)
    def divided(a):
        return EP.term(2*d,1) if a==0 else (EP.term(2*d-a)-EP.term(2*d))/a
    pair=2*k*k/d*(divided(2*d-g)-divided(d-g))
    joint=k/d*(eg-EP.term(g+d))
    m=m0*eg+lam*eg.integral()
    p=p0*ed+m0*h+lam*h.integral()
    a=m*m-m0*eg*eg
    b=m*p+m0*(joint-eg*h)+lam*joint.integral()
    c=p*p-p0*ed*ed+m0*(pair-h*h)+lam*pair.integral()
    return m,p,a,b,c

def reaction_generator(m,p,lam,kappa,gamma,delta):
    """Direct jump increments on five coordinate polynomials."""
    def f(m,p):return (m,p,m*(m-1),m*p,p*(p-1))
    old=f(m,p);out=[F(0)]*5
    events=[(1,0,F(lam)),(-1,0,F(gamma)*m),(0,1,F(kappa)*m),(0,-1,F(delta)*p)]
    for dm,dp,rate in events:
        if rate:
            new=f(m+dm,p+dp)
            for j in range(5):out[j]+=rate*(new[j]-old[j])
    return tuple(out)
