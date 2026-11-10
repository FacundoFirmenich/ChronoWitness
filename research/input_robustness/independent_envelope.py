"""Independent interval recurrences for one- and two-stage error filters.

No closed acquisition-kernel primitive is imported. Integrals follow from
integrated differential equations. Repeated rates use the Jordan limit.
"""
from fractions import Fraction as F
def plus(x,y):return x[0]+y[0],x[1]+y[1]
def times(x,a):return a*x[0],a*x[1]
def minus(x,y):return plus(x,times(y,-1))

def integrate(values,kappa,gamma,start,end):
    ek=F(2)**(-kappa);eg=F(2)**(-gamma)
    qk=(1-ek)/kappa;qg=(1-eg)/gamma
    h=((ek-eg)/(gamma-kappa),F(0)) if gamma!=kappa else (F(0),eg)
    u=F(0);v=(F(0),F(0));iu=v;iv=v
    for j,d in enumerate(values[:end]):
        unext=ek*u+d*qk
        uint=(u*qk-d*qk/kappa,d/kappa)
        vnext=plus(times(v,eg),plus((d*qg/kappa,F(0)),times(h,u-d/kappa)))
        vint=times(minus(uint,minus(vnext,v)),1/gamma)
        if j>=start:iu=plus(iu,uint);iv=plus(iv,vint)
        u=unext;v=vnext
    return iu,iv
