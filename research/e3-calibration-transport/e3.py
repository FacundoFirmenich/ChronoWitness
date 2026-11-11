"""Retrospective E3: grouped base fitting and early-only calibration decisions."""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
import benchmark as b

HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PROTOCOL.json').read_text())
OUT=HERE/'results'
METHODS=P['candidate_methods']

def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')

def select(stats):
    records=[]
    for lam in b.P['ridge_lambdas']:
        errors=[]
        for j,s in enumerate(stats):
            c,a=b.ridge([q for i,q in enumerate(stats) if i!=j],lam)
            errors.append(b.mse_from_stats(s,c,a))
        records.append(dict(lam=lam,mse=float(np.mean(errors))))
    chosen=min(records,key=lambda x:x['mse'])
    c,a=b.ridge(stats,chosen['lam'])
    return c,a,chosen['lam'],records

def calibrate(pred,y):
    pm,ym=float(pred.mean()),float(y.mean())
    pc,yc=pred-pm,y-ym
    v=float(pc@pc)
    slope=1.0 if v==0 else max(0.0,float(pc@yc)/v)
    result={'raw':(1.,0.),'offset':(1.,ym-pm),'nonnegative_affine':(slope,ym-slope*pm)}
    for method in METHODS[1:]:
        s,a=result[method]
        assert abs(float(np.mean(s*pred+a-y)))<1e-8
    return result

def decide(early_mse,threshold):
    if threshold=='always_raw' or early_mse['raw']==0:return 'raw'
    choice=min(METHODS,key=lambda m:early_mse[m])
    gain=1-early_mse[choice]/early_mse['raw']
    return choice if gain>threshold else 'raw'

def main():
    OUT.mkdir(exist_ok=False);start=time.monotonic()
    archive=Path(sys.argv[1]);hsh=hashlib.sha256()
    with archive.open('rb') as f:
        while chunk:=f.read(1048576):hsh.update(chunk)
    assert hsh.hexdigest()==P['archive_sha256']
    data=b.load(archive);train=b.P['train_dates'];test=b.P['test_dates']
    cases=[];fitrecords=[];windowrecords=[]
    reference=json.loads((HERE/'reference_models.json').read_text())
    refs={(x['offset'],x.get('horizon'),x['model']):x for x in reference if 'coef' in x}
    for offset in P['offsets']:
      for horizon in P['horizons']:
       for model in P['models']:
        stats=[]
        for date in train:
            d=data[date];cells,t,_=b.samples(d,horizon,offset)
            x=b.features(d,cells,t,horizon,offset,model)
            stats.append(b.sufficient(x,d['fluo1'][cells,t+horizon]-d['fluo1'][cells,t]))
        fits={}
        for j,date in enumerate(train):
            fitting=[x for i,x in enumerate(stats) if i!=j]
            fits[date]=select(fitting)
            assert date not in [x for i,x in enumerate(train) if i!=j]
            fitrecords.append(dict(date=date,role='training_oof',fitting_dates=[x for i,x in enumerate(train) if i!=j],offset=offset,horizon=horizon,model=model,coef=fits[date][0].tolist(),intercept=fits[date][1],selected_lambda=fits[date][2],inner_cv=fits[date][3]))
        final=select(stats);ref=refs[(offset,horizon,model)]
        assert np.allclose(final[0],ref['coef'],rtol=1e-10,atol=1e-8)
        assert np.isclose(final[1],ref['intercept'],rtol=1e-10,atol=1e-8)
        fitrecords.append(dict(date='original_test_fit',role='all_training',fitting_dates=train,offset=offset,horizon=horizon,model=model,coef=final[0].tolist(),intercept=final[1],selected_lambda=final[2],inner_cv=final[3]))
        for date in train+test:
            d=data[date];cells,t,availability=b.samples(d,horizon,offset)
            c,a=(fits[date] if date in train else final)[:2]
            pred=d['fluo1'][cells,t]+b.features(d,cells,t,horizon,offset,model)@c+a
            y=d['fluo1'][cells,t+horizon]
            fit=t+horizon<=P['early_fit_last_target']
            val=(t>=P['early_validation_first_origin'])&(t+horizon<=P['early_validation_last_target'])
            refit=t+horizon<=P['refit_last_target']
            late=t>=P['late_first_origin']
            assert all(x.any() for x in [fit,val,refit,late])
            assert max(t[fit]+horizon)<min(t[val]-11)
            assert max(t[refit]+horizon)<min(t[late]-11)
            early=calibrate(pred[fit],y[fit]);full=calibrate(pred[refit],y[refit])
            early_mse={m:float(np.mean((s*pred[val]+q-y[val])**2)) for m,(s,q) in early.items()}
            # No late outcomes are passed to the decision function.
            case=dict(date=date,role='training_oof' if date in train else 'seen_test',offset=offset,horizon=horizon,model=model,
                early=early,full=full,early_mse=early_mse,pred=pred[late],target=y[late],origins=t[late])
            cases.append(case)
            windowrecords.append(dict(date=date,offset=offset,horizon=horizon,model=model,n_fit=int(fit.sum()),n_validation=int(val.sum()),n_refit=int(refit.sum()),n_late=int(late.sum()),latest_fit_target=int(max(t[fit]+horizon)),earliest_validation_feature=int(min(t[val]-11)),latest_refit_target=int(max(t[refit]+horizon)),earliest_late_feature=int(min(t[late]-11)),**availability))
        print(json.dumps(dict(stage='fitted',offset=offset,horizon=horizon,model=model)),flush=True)
    assert len(cases)==P['expected_cases']
    primary=lambda x:all(x[k]==v for k,v in P['primary'].items())
    tune=[x for x in cases if x['role']=='training_oof' and primary(x)]
    assert len(tune)==4
    risks=[]
    for threshold in P['thresholds_relative_early_MSE_gain']:
        rows=[]
        for x in tune:
            choice=decide(x['early_mse'],threshold);s,a=x['full'][choice]
            raw=float(np.mean((x['pred']-x['target'])**2));assert raw>0
            ratio=float(np.mean((s*x['pred']+a-x['target'])**2))/raw
            rows.append(dict(date=x['date'],choice=choice,mse_ratio=ratio))
        risks.append(dict(threshold=threshold,mean_ratio=float(np.mean([x['mse_ratio'] for x in rows])),worst_ratio=max(x['mse_ratio'] for x in rows),experiments=rows))
    order=lambda r:(r['mean_ratio'],r['worst_ratio'],-(float('inf') if r['threshold']=='always_raw' else r['threshold']))
    chosen=min(risks,key=order)['threshold']
    save('THRESHOLD_SELECTION.json',dict(chosen=chosen,training_only_risks=risks,primary=P['primary']))
    output=[];bins=[];decisions=[];sensitivity=[]
    for x in cases:
        choice=decide(x['early_mse'],chosen)
        identity={k:x[k] for k in ['date','role','offset','horizon','model']}
        decisions.append(dict(**identity,choice=choice,threshold=chosen,early_validation_mse=x['early_mse'],early_fit=x['early'],refit=x['full']))
        parameters={**x['full'],'gated_refit':x['full'][choice],'gated_frozen':x['early'][choice]}
        for method,(s,a) in parameters.items():
            pred=s*x['pred']+a
            output.append(dict(**identity,method=method,n=len(pred),**b.metrics(pred,x['target'])))
            for low,high in P['late_origin_bins']:
                mask=(x['origins']>=low)
                if high is not None:mask&=x['origins']<=high
                record=dict(**identity,method=method,first_origin=low,last_origin=high,n=int(mask.sum()))
                if mask.any():record.update(b.metrics(pred[mask],x['target'][mask]))
                else:record['status']='NO_ELIGIBLE_WINDOWS'
                bins.append(record)
        if x['role']=='seen_test' and primary(x):
            for threshold in P['thresholds_relative_early_MSE_gain']:
                method=decide(x['early_mse'],threshold);s,a=x['full'][method]
                sensitivity.append(dict(**identity,threshold=threshold,choice=method,**b.metrics(s*x['pred']+a,x['target'])))
    assert len(output)==P['expected_metric_rows']
    for name,value in [('METRICS.json',output),('TEMPORAL_BINS.json',bins),('DECISIONS.json',decisions),('WINDOWS.json',windowrecords),('BASE_FITS.json',fitrecords),('THRESHOLD_SENSITIVITY.json',sensitivity)]:save(name,value)
    # Compare raw and static E3 corrections to unchanged E2 at cutoff120.
    e2=json.loads((HERE/'reference_e2_metrics.json').read_text())
    previous={(r['date'],r['offset'],r['horizon'],r['model'],r['method']):r for r in e2 if r['cutoff']==120}
    compared=0
    for r in output:
        if r['role']!='seen_test' or r['method'] not in METHODS:continue
        v=previous[(r['date'],r['offset'],r['horizon'],r['model'],r['method'])]
        assert r['n']==v['n']
        for k in ['rmse','mae','bias']:assert np.isclose(r[k],v[k],rtol=1e-10,atol=1e-8),(r,k,v[k])
        compared+=1
    assert compared==162
    save('RUN.json',dict(status='COMPLETE_RETROSPECTIVE_E3_A',elapsed_seconds=time.monotonic()-start,metric_rows=len(output),cases=len(cases),chosen_threshold=chosen,static_E2_rows_reproduced=compared,grouped_base_exclusion='PASS',temporal_separation='PASS',all_four_base_fit_matches_E1='PASS',archive_sha256=hsh.hexdigest(),protocol_sha256=hashlib.sha256((HERE/'PROTOCOL.json').read_bytes()).hexdigest(),direct_FD7_validation=False))
    print(json.dumps(dict(status='COMPLETE_RETROSPECTIVE_E3_A',chosen_threshold=chosen,seconds=time.monotonic()-start)),flush=True)

if __name__=='__main__':main()
