"""E11 causal, cell-local calibration. Original ChronoWitness code, MIT."""
import numpy as np
from numba import njit

CANDIDATES=[{'id':f'w{w}_{family}_s{int(g*100)}','lookback':w,'nested':family=='nested','shrink':g}
 for w in (180,360) for family in ('cell','nested') for g in (.25,.5)]

@njit(cache=True)
def q95_abs(x,n,c):
 a=np.empty(n)
 for j in range(n):a[j]=abs(x[j]-c)
 a.sort();v=.95*(n-1);k=int(v);return a[k]+(v-k)*(a[min(k+1,n-1)]-a[k])

@njit(cache=True)
def causal(t,e,pulse,band,late,h):
 n=len(t);correction=np.zeros((n,8));level=np.full((n,8),-1,np.int8);support=np.zeros((n,8),np.int16);last_target=np.full((n,8),-1,np.int64);reason=np.zeros((n,8),np.int8)
 for i in range(n):
  if not late[i]:continue
  for wi in range(2):
   lookback=180 if wi==0 else 360
   for family in range(2):
    chosen=np.empty(12,np.int64);count=0;lev=-1
    # Highest supported jurisdiction, irrespective of its eventual sign/tail result.
    for candidate_level in range(2 if family==1 else 0,-1,-1):
     count=0;last=10**12
     for j in range(i-1,-1,-1):
      if t[j]<t[i]-lookback:break
      if t[j]+h>=t[i] or last-t[j]<h:continue
      if candidate_level>=1 and pulse[j]!=pulse[i]:continue
      if candidate_level==2 and band[j]!=band[i]:continue
      chosen[count]=j;last=t[j];count+=1
      if count==12:break
     if count>=6:lev=candidate_level;break
    k=wi*4+family*2
    if lev<0:continue
    split=count//2;older=np.empty(12);recent=np.empty(12)
    # chosen is newest first; split into chronological older/recent blocks.
    for a in range(split):older[a]=e[chosen[count-1-a]]
    for a in range(count-split):recent[a]=e[chosen[count-split-1-a]]
    mu1=np.mean(older[:split]);mu2=np.mean(recent[:count-split])
    for gi in range(2):
     j=k+gi;level[i,j]=lev;support[i,j]=count;last_target[i,j]=t[chosen[0]]+h
     if mu1*mu2<=0:reason[i,j]=1;continue
     gamma=.25 if gi==0 else .5
     c=gamma*np.sign(mu2)*min(abs(mu1),abs(mu2))
     if q95_abs(older,split,c)>1.01*q95_abs(older,split,0.) or q95_abs(recent,count-split,c)>1.01*q95_abs(recent,count-split,0.):reason[i,j]=2;continue
     correction[i,j]=c;reason[i,j]=3
 return correction,level,support,last_target,reason

def reference_one(t,e,pulse,band,i,h,p):
 """Independent readable implementation for actual-observation audit queries."""
 for lev in ([2,1,0] if p['nested'] else [0]):
  indices=[]
  for j in range(i-1,-1,-1):
   if t[j]<t[i]-p['lookback']:break
   if t[j]+h>=t[i]:continue
   if indices and t[indices[-1]]-t[j]<h:continue
   if lev>=1 and pulse[j]!=pulse[i]:continue
   if lev==2 and band[j]!=band[i]:continue
   indices.append(j)
   if len(indices)==12:break
  if len(indices)>=6:break
 else:return 0.,-1,0,-1,0
 chronological=list(reversed(indices));m=len(indices)//2
 a=np.array([e[j] for j in chronological[:m]]);b=np.array([e[j] for j in chronological[m:]])
 r=(lev,len(indices),int(t[indices[0]]+h))
 if np.mean(a)*np.mean(b)<=0:return (0.,*r,1)
 c=p['shrink']*np.sign(np.mean(b))*min(abs(np.mean(a)),abs(np.mean(b)))
 if np.quantile(abs(a-c),.95)>1.01*np.quantile(abs(a),.95) or np.quantile(abs(b-c),.95)>1.01*np.quantile(abs(b),.95):return (0.,*r,2)
 return (float(c),*r,3)
