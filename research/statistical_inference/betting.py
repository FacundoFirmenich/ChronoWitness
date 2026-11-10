"""Exact bounded-score e-process arithmetic, not a physical qualification service.

R, tolerance and stakes must be fixed before the current block is revealed.
The caller must establish the conditional-mean and range contracts in SI S12.
No range, calibration, independent unit or biological parameter is inferred here.
"""
from fractions import Fraction as F

STAKES = (F(1, 8), F(1, 4), F(1, 2), F(1))

def initial(stakes=STAKES):
    if not stakes or any(not 0 <= q <= 1 for q in stakes):
        raise ValueError('Stakes must lie in [0,1]')
    return tuple(F(1) for _ in range(2 * len(stakes)))

def update(capital, x, radius, tolerance, stakes=STAKES):
    x, radius, tolerance = map(F, (x, radius, tolerance))
    if radius <= 0 or tolerance < 0 or abs(x) > radius:
        raise ValueError('Invalid or violated bounded-score contract')
    if len(capital) != 2 * len(stakes) or any(c < 0 for c in capital):
        raise ValueError('Invalid capital vector')
    if any(not 0 <= q <= 1 for q in stakes):
        raise ValueError('Stake outside [0,1]')
    factors = [1 + q * (s*x - tolerance)/(radius + tolerance)
               for s in (1, -1) for q in stakes]
    assert all(f >= 0 for f in factors)
    return tuple(c*f for c, f in zip(capital, factors))

def evidence(capital):
    return sum(capital, F(0))/len(capital)

def endpoint_box_budget(ell, duration, mean_radius, start_radii, end_radii):
    ell = tuple(map(F, ell)); start_radii = tuple(map(F, start_radii)); end_radii = tuple(map(F, end_radii))
    duration, mean_radius = F(duration), F(mean_radius)
    if duration <= 0 or mean_radius < 0 or len(ell) != len(start_radii) or len(ell) != len(end_radii):
        raise ValueError('Invalid endpoint contract')
    if any(v < 0 for v in start_radii + end_radii):
        raise ValueError('Negative uncertainty radius')
    return mean_radius + sum(abs(l)*(a+b) for l,a,b in zip(ell,start_radii,end_radii))/duration

def randomized_pair_tolerance(potential_budgets):
    """Four externally valid bounds: units 1,2 under both assignments a,b."""
    values=tuple(map(F,potential_budgets))
    if len(values)!=4 or any(v<0 for v in values):
        raise ValueError('Four nonnegative potential-outcome budgets required')
    return sum(values)/2
