"""Exact two-state probabilistic-reader stress test; no biological observations."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
WORDS = ('101111110010110010001000', '100010110010111111001000')

def periodic_profile(word, theta):
    # theta=(P(1|0,0),P(1|1,0),P(1|0,1),P(1|1,1)); row stochastic.
    a = (theta[0], theta[2])
    b = (theta[1]-theta[0], theta[3]-theta[2])
    intercept, slope = F(0), F(1)
    for bit in map(int, word):
        intercept, slope = a[bit]+b[bit]*intercept, b[bit]*slope
    if slope == 1:
        return None  # nonunique block fixed point: outside this stress test
    p = intercept/(1-slope)
    start = p
    profile = [F(0)]*4
    for z in map(int, word):
        profile[z] += 1-p
        profile[2+z] += p
        p = a[z]+b[z]*p
    assert p == start and sum(profile) == len(word)
    return tuple(x/len(word) for x in profile)

def main():
    grid = [F(i,4) for i in range(5)]
    tested = skipped = separated = 0
    witness = None
    for theta in product(grid, repeat=4):
        pa, pb = (periodic_profile(w, theta) for w in WORDS)
        if pa is None or pb is None:
            skipped += 1
            continue
        tested += 1
        if pa != pb:
            separated += 1
            if witness is None:
                witness = dict(theta=list(map(str,theta)), profile_A=list(map(str,pa)),
                               profile_B=list(map(str,pb)),
                               state_1_contrast=str(sum(pa[2:])-sum(pb[2:])))
    result = dict(scope='Exact rational parameter grid, not all stochastic readers',
                  grid=list(map(str,grid)), tested=tested, skipped_nonunique=skipped,
                  separating_profiles=separated, first_witness=witness,
                  biological_data=False)
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/STOCHASTIC_GRID.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
