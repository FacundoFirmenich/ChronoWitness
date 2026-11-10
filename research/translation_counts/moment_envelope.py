"""Positive moment envelope for explicit transcription/translation (SI S14).

Order: E M, E P, E M(M-1), E MP, E P(P-1). Bounds are external contracts.
"""
from fractions import Fraction as F
from exp_polynomial import EP

def drift(y,lam,kappa,gamma,delta):
    m,p,a,b,c=y
    return (lam-gamma*m,kappa*m-delta*p,2*lam*m-2*gamma*a,
            lam*p+kappa*(a+m)-(gamma+delta)*b,2*kappa*b-2*delta*c)

def linear_ode(rate,forcing,initial):
    """Exact solution y'+rate*y=forcing; generic resonances included."""
    rate=F(rate);result=EP.term(rate,0,initial)
    for (r,k),c in forcing.terms.items():
        d=rate-r
        if d==0:result+=EP.term(rate,k+1,c/F(k+1));continue
        value=c/d;part=EP.term(r,k,value)
        for j in range(k-1,-1,-1):
            value=-F(j+1)*value/d;part+=EP.term(r,j,value)
        result+=part-EP.term(rate,0,part.at_zero())
    return result

def propagate(initial,lam,kappa,gamma,delta):
    initial=tuple(map(F,initial));lam,kappa,gamma,delta=map(F,(lam,kappa,gamma,delta))
    if len(initial)!=5 or min(*initial,lam,kappa,gamma,delta)<0:
        raise ValueError('Five nonnegative initial moment bounds and rates required')
    m=linear_ode(gamma,EP.lift(lam),initial[0])
    p=linear_ode(delta,kappa*m,initial[1])
    a=linear_ode(2*gamma,2*lam*m,initial[2])
    b=linear_ode(gamma+delta,lam*p+kappa*(a+m),initial[3])
    c=linear_ode(2*delta,2*kappa*b,initial[4])
    return m,p,a,b,c

def stationary(lam,kappa,gamma,delta):
    lam,kappa,gamma,delta=map(F,(lam,kappa,gamma,delta))
    if min(lam,kappa,gamma,delta)<=0:
        raise ValueError('Strictly positive rates required for this supersolution')
    m=lam/gamma;p=kappa*m/delta;a=m*m
    b=m*p+kappa*m/(gamma+delta);c=kappa*b/delta
    return m,p,a,b,c

def uniform_envelope(initial,lam,kappa,gamma,delta):
    initial=tuple(map(F,initial))
    if len(initial)!=5 or min(initial)<0:raise ValueError('Invalid initial moments')
    v=stationary(lam,kappa,gamma,delta)
    eta=max(F(1),*(a/b for a,b in zip(initial,v)))
    return eta,tuple(eta*b for b in v)

def deterministic_initial(m,p):
    if not isinstance(m,int) or not isinstance(p,int) or min(m,p)<0:
        raise ValueError('Nonnegative integer initial populations required')
    return tuple(map(F,(m,p,m*(m-1),m*p,p*(p-1))))

def saturation_budget(curves,start,end,cap_m,cap_p,kappa,gamma,delta):
    """Certified upper loss for raw and endpoint-corrected protein readout.

    Time arguments are integer multiples of log(2). Returned fractions are
    rigorous upper bounds; parameters/caps are not estimates or defaults.
    """
    start,end,cm,cp,k,g,d=map(F,(start,end,cap_m,cap_p,kappa,gamma,delta))
    if start<0 or end<=start or min(cm,cp,g,d)<=0 or k<0:raise ValueError('Invalid readout contract')
    from exp_polynomial import log2_interval
    hlo=(end-start)*log2_interval()[0]
    m,p,a,b,c=curves;qm=m+a;qp=p+c
    def upper(f,t):return max(F(0),f.log2_interval(t)[1])
    def integrated_upper(f):
        f=f.integral();return max(F(0),f.log2_interval(end)[1]-f.log2_interval(start)[0])
    raw=min(integrated_upper(p),integrated_upper(qp)/(4*cp))/hlo
    loss_m=sum(min(upper(m,t),upper(qm,t)/(4*cm)) for t in (start,end))
    loss_p=sum(min(upper(p,t),upper(qp,t)/(4*cp)) for t in (start,end))
    corrected=raw+k/(g*d*hlo)*loss_m+loss_p/(d*hlo)
    radius=cp+2*(k*cm/(g*d)+cp/d)/hlo
    return raw,corrected,radius
