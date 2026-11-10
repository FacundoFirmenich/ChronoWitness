"""Frozen finite numerical search; candidates require separate rational certification."""
from pathlib import Path
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import json,hashlib,time
import numpy as np
from scipy.linalg import expm
from scipy.optimize import differential_evolution
P=Path(__file__).parent;O=P.parent/'results';O.mkdir(exist_ok=True)
protocol=json.loads((P/'PROTOCOL.json').read_text());WORDS=('101111110010110010001000','100010110010111111001000')
OFF=[(i,j) for i in range(3) for j in range(3) if i!=j]
def generators(rates):
    qs=[]
    for block in np.reshape(rates,(2,6)):
        q=np.zeros((3,3))
        for (i,j),x in zip(OFF,block):q[i,j]=x
        q[np.diag_indices(3)]=-q.sum(axis=1);qs.append(q)
    return qs

def occupations(qs):
    ops=[]
    for q in qs:
        b=np.zeros((6,6));b[:3,:3]=q;b[:3,3:]=np.eye(3);e=expm(b);ops.append((e[:3,:3],e[:3,3:]))
    values=[]
    for word in WORDS:
        b=np.eye(3);j=np.zeros((3,3))
        for z in map(int,word):
            t,k=ops[z];j+=b@k;b=b@t
        a=(b.T-np.eye(3));a[2,:]=1;p=np.linalg.solve(a,[0,0,1])
        assert min(p)>-1e-10 and abs(p.sum()-1)<1e-10
        values.append(p@j/24)
    return np.array(values)

def main():
    starts=time.time();records=[]
    def objective(x):return -abs(np.diff(occupations(generators(np.exp(x))),axis=0)[0,0])
    for seed in protocol['seeds']:
        result=differential_evolution(objective,[(np.log(1/64),np.log(4))]*12,seed=seed,maxiter=protocol['maxiter'],popsize=protocol['popsize'],tol=protocol['tol'],polish=True,workers=1)
        rates=np.exp(result.x);den=protocol['quantization_denominator'];integers=np.rint(rates*den).astype(int);assert min(integers)>=den//64 and max(integers)<=4*den
        q=generators(integers/den);v=occupations(q)
        record=dict(seed=seed,success=bool(result.success),message=str(result.message),iterations=int(result.nit),evaluations=int(result.nfev),numerical_objective=float(-result.fun),rates_numerators=integers.tolist(),denominator=den,quantized_occupations=v.tolist(),quantized_contrast=(v[0]-v[1]).tolist())
        records.append(record);print(json.dumps(record),flush=True)
    best=max(records,key=lambda r:abs(r['quantized_contrast'][0]))
    baseline=[np.array([[-2,1,1],[1,-5,4],[1,4,-5]])/3*np.log(2),np.array([[-2,1,1],[4,-5,1],[1,1,-2]])/3*np.log(2)]
    out=dict(status='NUMERICAL_SEARCH_REQUIRES_CERTIFICATION',protocol_sha256=hashlib.sha256((P/'PROTOCOL.json').read_bytes()).hexdigest(),records=records,selected=best,baseline=(occupations(baseline)[0]-occupations(baseline)[1]).tolist(),elapsed_seconds=time.time()-starts)
    (O/'DESIGN_SEARCH.json').write_text(json.dumps(out,indent=2)+'\n');print('Selected',best['seed'],best['quantized_contrast'],flush=True)
if __name__=='__main__':main()
