"""Certified conditional count envelopes. No parameters are fitted or inferred.

All inputs are externally justified, predictable contracts (SI S13).
Fractions and outward rounding preserve inequalities, including exp evaluation.
"""
from fractions import Fraction as F
from functools import lru_cache

SCALE = 10**24

def outward(lo, hi):
    lo, hi = F(lo), F(hi)
    return F((lo*SCALE).__floor__(), SCALE), F((hi*SCALE).__ceil__(), SCALE)

@lru_cache(None)
def exp_interval(x):
    x = F(x)
    if x < 0:
        raise ValueError('Nonnegative exponent required')
    if x == 0:
        return F(1), F(1)
    term = total = F(1)
    for n in range(1, 10001):
        term *= x/n
        total += term
        if x < n+2:
            tail = term*x/(n+1)/(1-x/(n+2))
            if tail <= F(1, 10**28):
                return outward(total, total+tail)
    raise ArithmeticError('Exponential enclosure did not converge')

def geometric_pgf(u, p):
    u, p = F(u), F(p)
    if u <= 1 or not 0 <= p < 1 or p*u >= 1:
        raise ValueError('PGF requires u>1 and p*u<1')
    return (1-p)*u/(1-p*u)

def compound_pgf_upper(initial_cap, arrival_mass, u, burst_pgf):
    """N0 <= initial_cap; independent dominating marked Poisson arrivals."""
    n, mass, u, j = initial_cap, F(arrival_mass), F(u), F(burst_pgf)
    if not isinstance(n, int) or n < 0 or mass < 0 or u <= 1 or j < 1:
        raise ValueError('Invalid initial/arrival/PGF contract')
    return u**n * exp_interval(mass*(j-1))[1]

def compound_moments(initial_cap, arrival_mass, burst_mean, burst_second):
    n, mass, a, b = F(initial_cap), F(arrival_mass), F(burst_mean), F(burst_second)
    if min(n,mass,a,b)<0 or b<a*a:
        raise ValueError('Invalid moment bounds')
    mean = n+mass*a
    return mean, mean*mean+mass*b

def pgf_stoploss(r, u, mgf_upper):
    """Upper bound for E[(D-r)+], integer D>=0 with E[u**D]<=mgf_upper."""
    r, u, mgf_upper = F(r), F(u), F(mgf_upper)
    if r < 0 or u <= 1 or mgf_upper < 1:
        raise ValueError('Invalid lattice stop-loss contract')
    m = r.__floor__(); fraction = r-m
    return mgf_upper/u**(m+1)*(1-fraction+1/(u-1))

def stoploss_bound(r, mean_upper, second_upper=None, pgf_bounds=()):
    r, mean_upper = F(r), F(mean_upper)
    if r < 0 or mean_upper < 0:
        raise ValueError('Nonnegative threshold and mean required')
    candidates = [mean_upper]
    if second_upper is not None:
        second_upper = F(second_upper)
        if second_upper < 0:
            raise ValueError('Negative second moment')
        if r > 0:
            candidates.append(second_upper/(4*r))
    candidates.extend(pgf_stoploss(r,u,m) for u,m in pgf_bounds)
    return min(candidates)

def score_clipping_bias(cap, scale, offset, stoploss):
    """If |Z|<=scale*D+offset, return threshold r and L*stoploss(r)."""
    cap, scale, offset = map(F,(cap,scale,offset))
    if scale <= 0 or offset < 0 or cap < offset:
        raise ValueError('Require L>0 and cap>=offset>=0')
    r=(cap-offset)/scale
    return r, scale*stoploss(r)

def detector_contract(c, ell, duration, caps, losses):
    """Ideal coordinate saturation before averaging and endpoint correction.

    Returns arm [lower, upper] and mean distortion bound. No independence of
    channels, endpoints or frames is assumed. C must be nonnegative.
    """
    c,ell,caps,losses = [tuple(map(F,v)) for v in (c,ell,caps,losses)]
    h=F(duration)
    if h<=0 or not c or len({len(c),len(ell),len(caps),len(losses)})!=1:
        raise ValueError('Invalid detector dimensions or duration')
    if any(v<0 for v in c+caps+losses):
        raise ValueError('Nonnegative detector coefficients/caps/losses required')
    endpoint=sum(abs(a)*b/h for a,b in zip(ell,caps))
    upper=sum(a*b for a,b in zip(c,caps))+endpoint
    bias=sum((a+2*abs(b)/h)*v for a,b,v in zip(c,ell,losses))
    return -endpoint, upper, bias

def contrast_contract(arm_a, arm_b, latent_tolerance, error_radius=0, error_mean=0):
    lo_a, hi_a, b_a=map(F,arm_a);lo_b,hi_b,b_b=map(F,arm_b)
    t,e,m=map(F,(latent_tolerance,error_radius,error_mean))
    if min(t,e,m,b_a,b_b)<0 or m>e or lo_a>hi_a or lo_b>hi_b:
        raise ValueError('Invalid contrast contract')
    return max(abs(lo_a-hi_b),abs(hi_a-lo_b))+e, t+b_a+b_b+m
