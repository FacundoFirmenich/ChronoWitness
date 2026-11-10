"""Closed count-product construction and integer path counting.

Does not import the sequential update implementation. Only constant-stake,
constant-radius/tolerance binary laws are handled by this independent checker.
"""
from fractions import Fraction as F
from math import comb

def capital_from_counts(n, positives, tolerance, stakes):
    t=F(tolerance)
    values=[]
    for direction in (1,-1):
        for q in stakes:
            up=1+q*(direction-t)/(1+t)
            down=1+q*(-direction-t)/(1+t)
            values.append(up**positives*down**(n-positives))
    return sum(values)/len(values)

def first_cross_counts(horizon, alpha, tolerance, stakes, exact_binomial=False):
    """Number of still-unrejected binary paths at each count, integer only."""
    live={0:1}; rejected=0; rows=[]
    for n in range(1,horizon+1):
        nxt={}
        for k,count in live.items():
            for new_k in (k,k+1):nxt[new_k]=nxt.get(new_k,0)+count
        rejected*=2
        for k in list(nxt):
            if exact_binomial:
                tail=F(2*sum(comb(n,j) for j in range(max(k,n-k),n+1)),2**n)
                crossing=tail<=alpha
            else:crossing=capital_from_counts(n,k,tolerance,stakes)>=1/alpha
            if crossing:rejected+=nxt.pop(k)
        live=nxt
        assert sum(live.values())+rejected==2**n
        rows.append(F(rejected,2**n))
    return rows
