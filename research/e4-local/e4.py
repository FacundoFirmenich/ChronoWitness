from pathlib import Path
import hashlib,json,sys,time,math
import numpy as np
import benchmark as b
HERE=Path(__file__).parent;P=json.loads((HERE/'PROTOCOL.json').read_text());OUT=HERE/'results'
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def support(c,t,mask):
    r=dict(windows=int(mask.sum()),distinct_trajectories=len(np.unique(c[mask])),distinct_origins=len(np.unique(t[mask])))
    r['qualified']=all(r[k]>=v for k,v in P['minimum_support'].items());return r
def fit(p,y):
    pm,ym=float(p.mean()),float(y.mean());pc=p-pm;v=float(pc@pc)
    s=1. if v==0 else max(0.,float(pc@(y-ym))/v)
    return {'raw':(1.,0.),'offset':(1.,ym-pm),'affine':(s,ym-s*pm)}
def metrics(p,y):
    e=p-y;a=np.abs(e);k=math.ceil(.05*len(a))
    return dict(mae=float(a.mean()),rmse=float(np.sqrt(np.mean(e*e))),bias=float(e.mean()),median_ae=float(np.median(a)),q90_ae=float(np.quantile(a,.9)),q95_ae=float(np.quantile(a,.95)),tail05_mean=float(np.sort(a)[-k:].mean()))
def label(g,eps):return 'LOCAL_OBSERVED_GAIN' if g>eps else 'LOCAL_OBSERVED_LOSS' if g< -eps else 'PRACTICAL_TIE'
def main():
    start=time.monotonic();OUT.mkdir(exist_ok=False)
    archive=Path(sys.argv[1]);hs=hashlib.sha256()
    with archive.open('rb') as f:
        while q:=f.read(1048576):hs.update(q)
    assert hs.hexdigest()==P['archive_sha256']
    data=b.load(archive)
    refs=json.loads((HERE/'reference_models.json').read_text());refs={(r['offset'],r.get('horizon'),r['model']):r for r in refs if 'coef' in r}
    old=json.loads((HERE/'e3_decisions.json').read_text());old={(r['date'],r['offset'],r['horizon']):r for r in old if r['role']=='seen_test' and r['model']=='history_input'}
    oldmetrics=json.loads((HERE/'e3_metrics.json').read_text());oldmetrics={(r['date'],r['offset'],r['horizon'],r['method']):r for r in oldmetrics if r['role']=='seen_test' and r['model']=='history_input'}
    records=[];gates=[];cuts=[];globals_=[];partition_checks=[]
    for offset in P['offsets']:
      for h in P['horizons']:
        vals=[];weights=[]
        for date in b.P['train_dates']:
            d=data[date];c,t,_=b.samples(d,h,offset);v=d['fluo1'][c,t]
            vals.append(v);weights.append(np.full(len(v),1/len(v)))
        v=np.concatenate(vals);w=np.concatenate(weights);ix=np.argsort(v,kind='stable');cdf=np.cumsum(w[ix])/sum(w)
        q10,q90=[float(v[ix[np.searchsorted(cdf,q)]]) for q in P['intensity_quantiles']]
        assert q10<q90;cuts.append(dict(offset=offset,horizon=h,q10=q10,q90=q90,training_dates=b.P['train_dates']))
        for date in b.P['test_dates']:
            d=data[date];c,t,_=b.samples(d,h,offset);current=d['fluo1'][c,t];y=d['fluo1'][c,t+h]
            r=refs[(offset,h,'history_input')];pred=current+b.features(d,c,t,h,offset,'history_input')@np.array(r['coef'])+r['intercept']
            edge=(2*d['stims'][c,t+offset-1]+d['stims'][c,t+offset]).astype(int)
            band=np.where(current<=q10,0,np.where(current>q90,2,1))
            fitmask=t+h<=72;valmask=(t>=84)&(t+h<=120);refmask=t+h<=120;late=t>=132
            assert max(t[fitmask]+h)<min(t[valmask]-11) and max(t[refmask]+h)<min(t[late]-11)
            glob=old[(date,offset,h)];params=glob['refit'];gc=glob['choice']
            policy={'raw':pred.copy(),'global_offset':params['offset'][0]*pred+params['offset'][1],'global_affine':params['nonnegative_affine'][0]*pred+params['nonnegative_affine'][1],'global_gate_E3':params[gc][0]*pred+params[gc][1]}
            for name in ['local_offset','local_affine','local_equalmix','local_gate']:policy[name]=pred.copy()
            context_support={}
            for e in range(4):
              for bi in range(3):
                context=(edge==e)&(band==bi);sf=support(c,t,context&fitmask);sv=support(c,t,context&valmask)
                qualified=sf['qualified'] and sv['qualified'];context_support[(e,bi)]=qualified
                record=dict(date=date,offset=offset,horizon=h,edge=f'{e//2}{e%2}',band=['low','middle','high'][bi],fit_support=sf,validation_support=sv,choice='raw',status='SUPPORTED' if qualified else 'OUT_OF_SUPPORT')
                if qualified:
                    early=fit(pred[context&fitmask],y[context&fitmask]);full=fit(pred[context&refmask],y[context&refmask])
                    losses={k:float(np.mean(np.abs(s*pred[context&valmask]+a-y[context&valmask]))) for k,(s,a) in early.items()}
                    choice=min(['raw','offset','affine'],key=lambda k:losses[k]);gain=0 if losses['raw']==0 else 1-losses[choice]/losses['raw']
                    if gain<=.01:choice='raw'
                    po=full['offset'][0]*pred[context]+full['offset'][1];pa=full['affine'][0]*pred[context]+full['affine'][1]
                    policy['local_offset'][context]=po;policy['local_affine'][context]=pa
                    policy['local_equalmix'][context]=(pred[context]+po+pa)/3
                    policy['local_gate'][context]=full[choice][0]*pred[context]+full[choice][1]
                    record.update(choice=choice,early_mae=losses,refit=full)
                gates.append(record)
            ident=dict(date=date,offset=offset,horizon=h)
            for name,pp in policy.items():
                mm=metrics(pp[late],y[late]);globals_.append(dict(**ident,policy=name,n=int(late.sum()),**mm))
                previous={'raw':'raw','global_offset':'offset','global_affine':'nonnegative_affine','global_gate_E3':'gated_refit'}.get(name)
                if previous:
                    oldm=oldmetrics[(date,offset,h,previous)]
                    for k in ['mae','rmse','bias']:assert np.isclose(mm[k],oldm[k],rtol=1e-10,atol=1e-8)
            local_case=[]
            for lo,hi in P['late_segments']:
              segment=late&(t>=lo)
              if hi is not None:segment&=t<=hi
              for e in range(4):
               for bi in range(3):
                mask=segment&(edge==e)&(band==bi);ss=support(c,t,mask);qualified=context_support[(e,bi)]
                raw=metrics(pred[mask],y[mask]) if mask.any() else None
                for name,pp in policy.items():
                    rr=dict(**ident,segment_start=lo,segment_end=hi,edge=f'{e//2}{e%2}',band=['low','middle','high'][bi],policy=name,support=ss,calibration_support=qualified,status='SUPPORTED' if ss['qualified'] else 'NOT_ESTIMABLE')
                    if name.startswith('local_') and not qualified and ss['qualified']:rr['status']='OUT_OF_SUPPORT'
                    if mask.any():
                        mm=metrics(pp[mask],y[mask]);rr.update(mm)
                        gain=0. if raw['mae']==0 and mm['mae']==0 else (None if raw['mae']==0 else 1-mm['mae']/raw['mae'])
                        rr['relative_MAE_gain']=gain
                        rr['label']=label(gain,.01) if rr['status']=='SUPPORTED' and gain is not None else rr['status']
                        rr['sensitivity_labels']={str(eps):label(gain,eps) for eps in [.001,.05]} if rr['status']=='SUPPORTED' and gain is not None else {}
                    else:rr['label']='NOT_ESTIMABLE'
                    records.append(rr);local_case.append(rr)
            for name,pp in policy.items():
                rr=[r for r in local_case if r['policy']==name and r['support']['windows']>0];n=sum(r['support']['windows'] for r in rr)
                assert n==int(late.sum());mm=metrics(pp[late],y[late])
                for k in ['mae','bias']:
                    assert np.isclose(sum(r[k]*r['support']['windows'] for r in rr)/n,mm[k],rtol=1e-12,atol=1e-9)
                assert np.isclose(sum(r['rmse']**2*r['support']['windows'] for r in rr)/n,mm['rmse']**2,rtol=1e-12,atol=1e-8)
            partition_checks.append(dict(**ident,status='PASS_EXACT_PARTITION_RECONSTRUCTION'))
            print(json.dumps(dict(stage='local_complete',**ident)),flush=True)
    assert len(records)==P['expected_metric_rows']
    for n,x in [('LOCAL_METRICS.json',records),('GLOBAL_CONTEXT.json',globals_),('LOCAL_DECISIONS.json',gates),('TRAINING_CUTS.json',cuts),('PARTITION_CHECKS.json',partition_checks)]:save(n,x)
    save('RUN.json',dict(status='COMPLETE_RETROSPECTIVE_E4_LOCAL',metric_rows=len(records),jurisdictions=len(records)//len(P['policies']),decisions=len(gates),seconds=time.monotonic()-start,protocol_sha256=hashlib.sha256((HERE/'PROTOCOL.json').read_bytes()).hexdigest(),direct_FD7_validation=False,global_authority=False))
if __name__=='__main__':main()
