"""Frozen E1 external-data observation benchmark; grouped validation, no imputation."""
from pathlib import Path
import csv
import hashlib
import io
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile
import numpy as np
from scipy.optimize import lsq_linear

HERE = Path(__file__).resolve().parent
P = json.loads((HERE/'BENCHMARK_PROTOCOL.json').read_text())
OUT = HERE/'benchmark_results'
MODELS = ['history_no_input', 'history_input', 'history_context']

def write(name, data):
    (OUT/name).write_text(json.dumps(data, indent=2, allow_nan=False)+'\n')

def download():
    path = Path(tempfile.gettempdir())/'chronowitness-E1-datasets.zip'
    assert not path.exists()
    assert shutil.disk_usage(path.parent).free > 2_000_000_000
    digest, sha, size = hashlib.md5(), hashlib.sha256(), 0
    url='https://zenodo.org/api/records/8114649/files/datasets.zip/content'
    with urllib.request.urlopen(url, timeout=120) as response, path.open('xb') as f:
        while chunk := response.read(1024*1024):
            f.write(chunk); digest.update(chunk); sha.update(chunk); size += len(chunk)
    assert size == P['archive_bytes'] and digest.hexdigest() == P['archive_md5']
    return path, sha.hexdigest()

def load(path):
    datasets = {}
    with zipfile.ZipFile(path) as z:
        for date in P['train_dates']+P['test_dates']:
            folder = next(n.rsplit('/',1)[0] for n in z.namelist() if date in n and n.endswith('/stims.npy'))
            d = {key: np.load(io.BytesIO(z.read(folder+'/'+key+'.npy')),allow_pickle=False)[:,:,0].astype(float)
                 for key in ['stims','fluo1','area','cell_count','neighbor_stims']}
            assert len({a.shape for a in d.values()}) == 1
            d['valid'] = np.logical_and.reduce([np.isfinite(a) for a in d.values()]) & (d['area']>0) & (d['cell_count']>0)
            assert set(np.unique(d['stims'])) <= {0.,1.}
            datasets[date] = d
    return datasets

def features(d, cells, origins, h, offset, model):
    past = origins[:,None]+np.arange(-11,1)
    f = [d['fluo1'][cells[:,None],past]]
    if model != 'history_no_input':
        upast=origins[:,None]+offset+np.arange(-12,0)
        future=origins[:,None]+offset+np.arange(h)
        f += [d['stims'][cells[:,None],upast],d['stims'][cells[:,None],future]]
    if model == 'history_context':
        f += [np.log(d['area'][cells,origins])[:,None],
              np.log(d['area'][cells,origins]/d['area'][cells,origins-11])[:,None],
              d['cell_count'][cells,origins,None],
              d['neighbor_stims'][cells[:,None],upast].mean(axis=1)[:,None]]
    return np.concatenate(f,axis=1)

def samples(d,h,offset):
    n,t = d['fluo1'].shape
    origins = np.arange(P['origin_start'],t-h,P['origin_stride'])
    cells, origins = np.meshgrid(np.arange(n),origins,indexing='ij')
    cells,origins=cells.ravel(),origins.ravel()
    count=len(cells)
    cumulative=np.pad(np.cumsum(~d['valid'],axis=1),((0,0),(1,0)))
    ok=(cumulative[cells,origins+h+1]-cumulative[cells,origins-11])==0
    cells,origins=cells[ok],origins[ok]
    assert len(cells)>0
    # Both alignments use valid finite stimulus histories and the same response windows.
    assert origins.min()+offset-12>=0 and origins.max()+offset+h-1<t
    return cells,origins,dict(candidate_windows=count,retained_windows=len(cells),
        retained_trajectories=len(np.unique(cells)),
        retained_zero_fluorescence_targets=int((d['fluo1'][cells,origins+h]==0).sum()))

def sufficient(x,y):
    return dict(n=len(y),mx=x.mean(0),my=float(y.mean()),xx=x.T@x/len(y),xy=x.T@y/len(y),yy=float(y@y/len(y)))

def aggregate(stats):
    return {key:np.mean([s[key] for s in stats],axis=0) for key in ['mx','my','xx','xy','yy']}

def ridge(stats,lam):
    s=aggregate(stats);mu=s['mx'];target=s['my']
    covariance=s['xx']-np.outer(mu,mu)
    sd=np.sqrt(np.maximum(np.diag(covariance),0));sd[sd<1e-10]=1
    normalized=covariance/np.outer(sd,sd)
    coef=np.linalg.solve(normalized+lam*np.eye(len(sd)),(s['xy']-mu*target)/sd)/sd
    intercept=target-mu@coef
    return coef,float(intercept)

def mse_from_stats(s,coef,b):
    value=s['yy']+coef@s['xx']@coef+b*b+2*b*(s['mx']@coef)-2*coef@s['xy']-2*b*s['my']
    assert value > -1e-5
    return float(max(0,value))

def select(stats):
    records=[]
    for lam in P['ridge_lambdas']:
        errors=[]
        for j in range(4):
            c,b=ridge([s for i,s in enumerate(stats) if i!=j],lam)
            errors.append(mse_from_stats(stats[j],c,b))
        records.append(dict(lam=lam,fold_mse=errors,mean_mse=float(np.mean(errors))))
    choice=min(records,key=lambda x:x['mean_mse'])
    c,b=ridge(stats,choice['lam'])
    return c,b,choice['lam'],records

def relaxation(datasets,offset):
    gs=[];bs=[];counts={}
    for date in P['train_dates']:
        d=datasets[date];valid=d['valid'][:,36:-1]&d['valid'][:,37:]
        cells,t=np.nonzero(valid);t=t+36
        y=d['fluo1'][cells,t]/4095
        x=np.column_stack([y,np.ones(len(y)),d['stims'][cells,t+offset]])
        target=d['fluo1'][cells,t+1]/4095
        gs.append(x.T@x/len(y));bs.append(x.T@target/len(y));counts[date]=len(y)
    g,b=np.mean(gs,0),np.mean(bs,0)
    lower=np.linalg.cholesky(g)
    result=lsq_linear(lower.T,np.linalg.solve(lower,b),bounds=([0,-np.inf,-np.inf],[1,np.inf,np.inf]),tol=1e-12)
    assert result.success
    coef=result.x.copy();coef[1:]*=4095
    return coef,dict(coefficients=coef.tolist(),training_pairs=counts,optimality=float(result.optimality),rho_at_boundary=bool(coef[0]<1e-8 or coef[0]>1-1e-8))

def relax_predict(d,cells,t,h,offset,coef):
    rho,b,g=coef
    y=d['fluo1'][cells,t].copy()
    for j in range(h): y=rho*y+b+g*d['stims'][cells,t+j+offset]
    return y

def metrics(prediction,target):
    residual=prediction-target
    assert np.isfinite(residual).all()
    return dict(rmse=float(np.sqrt(np.mean(residual**2))),mae=float(np.mean(np.abs(residual))),bias=float(np.mean(residual)),predicted_negative=int((prediction<0).sum()),predicted_above_4095=int((prediction>4095).sum()))

def selfcheck():
    # Index-coded fixture tests causality; it is not a simulated scientific dataset.
    a=np.arange(80,dtype=float)[None,:]+1
    d={k:a.copy() for k in ['fluo1','area','cell_count','stims','neighbor_stims']}
    c,t=np.array([0]),np.array([36])
    for offset in [0,1]:
        f=features(d,c,t,6,offset,'history_context')
        changed={k:v.copy() for k,v in d.items()}
        for k in ['fluo1','area','cell_count','neighbor_stims']:changed[k][:,37:]+=500
        assert np.array_equal(f,features(changed,c,t,6,offset,'history_context'))
        assert f[0,24]==d['stims'][0,36+offset]
    x=np.arange(10,dtype=float).reshape(-1,1);y=3*x[:,0]+2
    c,b=ridge([sufficient(x,y)],1e-12)
    assert np.max(np.abs(x@c+b-y))<1e-9
    assert abs(mse_from_stats(sufficient(x,y),c,b)-np.mean((x@c+b-y)**2))<1e-9
    d['fluo1'][:]=2;d['stims'][:]=1
    assert np.allclose(relax_predict(d,np.array([0]),np.array([36]),6,1,[.5,1,0]),2)

def main():
    OUT.mkdir(exist_ok=True);selfcheck()
    path,archive_sha=download();datasets=load(path)
    output=[];selection=[];availability=[];coefficients=[];stratified=[]
    repeated={}
    for date,d in datasets.items():
        _,inverse,counts=np.unique(d['stims'],axis=0,return_inverse=True,return_counts=True)
        repeated[date]=counts[inverse]>=50
    # Complete all choices using training data before evaluating any test outcome.
    fitted={}
    for offset in P['alignment_offsets']:
        rc,rd=relaxation(datasets,offset);fitted[(offset,'relaxation')]=rc
        coefficients.append(dict(offset=offset,model='common_relaxation',**rd))
        for h in P['horizons_frames']:
            for model in MODELS:
                stats=[]
                for date in P['train_dates']:
                    d=datasets[date];cells,t,counts=samples(d,h,offset)
                    x=features(d,cells,t,h,offset,model)
                    y=d['fluo1'][cells,t+h]-d['fluo1'][cells,t]
                    stats.append(sufficient(x,y))
                c,b,lam,cv=select(stats);fitted[(offset,h,model)]=(c,b)
                selection.append(dict(offset=offset,horizon=h,model=model,selected_lambda=lam,cv=cv))
                coefficients.append(dict(offset=offset,horizon=h,model=model,coef=c.tolist(),intercept=b))
    write('TRAINING_SELECTION.json',selection);write('FITTED_MODELS.json',coefficients)
    for offset in P['alignment_offsets']:
        for h in P['horizons_frames']:
            for date in P['train_dates']+P['test_dates']:
                d=datasets[date];cells,t,counts=samples(d,h,offset)
                availability.append(dict(offset=offset,horizon=h,date=date,**counts))
                target=d['fluo1'][cells,t+h];current=d['fluo1'][cells,t]
                predictions={'persistence':current,'common_relaxation':relax_predict(d,cells,t,h,offset,fitted[(offset,'relaxation')])}
                for model in MODELS:
                    c,b=fitted[(offset,h,model)]
                    predictions[model]=current+features(d,cells,t,h,offset,model)@c+b
                for model,pred in predictions.items():
                    output.append(dict(offset=offset,horizon=h,date=date,split='test' if date in P['test_dates'] else 'train',model=model,n=len(target),**metrics(pred,target)))
                    if h==P['primary_horizon_frames']:
                        for label,mask in [('frequent_sequence',repeated[date][cells]),('other_sequence',~repeated[date][cells])]:
                            if mask.any():
                                stratified.append(dict(offset=offset,horizon=h,date=date,model=model,stratum=label,n=int(mask.sum()),**metrics(pred[mask],target[mask])))
    write('METRICS.json',output);write('WINDOW_AVAILABILITY.json',availability)
    write('INPUT_STRATA_METRICS.json',stratified)
    decisions={}
    for name,left,right in [('input_information','history_input','history_no_input'),('single_relaxation_adequacy','history_input','common_relaxation'),('context_information','history_context','history_input')]:
        comparisons=[]
        for offset in P['alignment_offsets']:
            for date in P['test_dates']:
                records={x['model']:x for x in output if x['offset']==offset and x['date']==date and x['horizon']==12}
                ratio=records[left]['rmse']/records[right]['rmse']
                comparisons.append(dict(offset=offset,date=date,rmse_ratio=ratio,relative_reduction=1-ratio,passes=ratio<=.95))
        decisions[name]=dict(passes_all=all(x['passes'] for x in comparisons),comparisons=comparisons)
    write('DECISIONS.json',decisions)
    with (OUT/'METRICS.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(output[0]));writer.writeheader();writer.writerows(output)
    write('RUN.json',dict(status='COMPLETE_FROZEN_E1',source_commit=os.environ.get('GITHUB_SHA'),protocol_sha256=hashlib.sha256((HERE/'BENCHMARK_PROTOCOL.json').read_bytes()).hexdigest(),archive_sha256=archive_sha,metric_rows=len(output),test_metric_rows=sum(x['split']=='test' for x in output),selection_rows=len(selection),selfchecks='PASS',statistical_inference='descriptive, grouped by experiment; no independence-based p values',direct_FD7_validation=False))
    print(json.dumps(decisions,indent=2))

if __name__=='__main__': main()
