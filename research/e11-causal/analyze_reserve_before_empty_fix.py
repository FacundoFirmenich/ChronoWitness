"""E11 held-out acquisition analysis. Original code MIT; no model selection here."""
from pathlib import Path
import json,hashlib,time,resource
import numpy as np,pandas as pd
R=Path('/content/chronowitness-e11-20261111');A=R/'analysis';A.mkdir(exist_ok=True)
def save(n,v):(A/n).write_text(json.dumps(v,indent=2,allow_nan=False))
def stats(e,v):
 b=float(np.mean(e*e));m=float(np.mean(v*v));q=float(np.quantile(abs(e),.95));p=float(np.quantile(abs(v),.95))
 return dict(n=len(e),base_mse=b,mse=m,delta_mse=m-b,base_q95=q,q95=p,rmse_ratio=float(np.sqrt(m/b)) if b else None,q95_ratio=p/q if q else None)
def main():
 start=time.monotonic();s=pd.DataFrame(json.loads((R/'RESERVE_SUMMARY.json').read_text()));nodes=[];checks=[];routes=[];cells=[]
 for f in sorted((R/'reserve').glob('*_atomic.csv.gz')):
  stem=f.name.removesuffix('_atomic.csv.gz');d=pd.read_csv(f);r=s[s.context==stem].iloc[0];ident={k:(r[k].item() if hasattr(r[k],'item') else r[k]) for k in ['context','file','date','family','horizon','alignment']}
  assert not d.duplicated(['track','origin']).any() and d.stage.eq('late').all()
  assert np.allclose(d.causal_error,d.history_input_error-d.causal_correction,rtol=0,atol=1e-12)
  assert (d.loc[d.policy_support>=6,'latest_feedback_target']<d.loc[d.policy_support>=6,'origin']).all()
  assert (d.loc[d.policy_reason==3,'policy_support']>=6).all()
  assert d.loc[d.policy_reason!=3,'causal_correction'].eq(0).all()
  first=int(d.origin.min());last=int(d.origin.max());d['segment']=np.minimum(2,(d.origin-first)*3//(last-first+1)).astype(int)
  for model,col in [('history_input','history_input_error'),('history_no_input','history_no_input_error'),('persistence','persistence_error'),('fixed_guard','fixed_guard_error'),('causal_selected','causal_error')]:
   e=d[col].to_numpy();row=s[(s.context==stem)&(s.model==model)].iloc[0]
   assert len(e)==row['n']
   for x,y in [(np.sqrt(np.mean(e*e)),row.rmse),(np.quantile(abs(e),.95),row.q95),(np.mean(abs(e)),row.mae),(np.mean(e),row.bias)]:assert abs(x-y)<1e-12
  for key,g in d.groupby(['policy_level','policy_reason'],observed=True):routes.append({**ident,'level':int(key[0]),'reason':int(key[1]),'n':len(g)})
  for tid,g in d.groupby('track'):
   row=stats(g.history_input_error.to_numpy(),g.causal_error.to_numpy());formula=float(np.mean(g.causal_correction**2-2*g.causal_correction*g.history_input_error))
   assert np.isclose(row['delta_mse'],formula,rtol=1e-9,atol=1e-13)
   cells.append({**ident,'track':int(tid),'status':'DESCRIPTIVE' if len(g)>=20 else 'LOW_SUPPORT',**row,'identity_delta':formula})
  for model,col in [('fixed_guard','fixed_guard_error'),('causal_selected','causal_error')]:
   parent=stats(d.history_input_error.to_numpy(),d[col].to_numpy());nodes.append({**ident,'model':model,'kind':'parent','labels':'{}','status':'DESCRIPTIVE' if len(d)>=20 else 'LOW_SUPPORT',**parent})
   for dims in [['pulse_band','value_band'],['segment'],['segment','pulse_band','value_band']]:
    children=[]
    for key,g in d.groupby(dims,observed=True):
     if not isinstance(key,tuple):key=(key,)
     row=stats(g.history_input_error.to_numpy(),g[col].to_numpy());labels={k:int(v) for k,v in zip(dims,key)}
     children.append(row);nodes.append({**ident,'model':model,'kind':'+'.join(dims),'labels':json.dumps(labels),'status':'DESCRIPTIVE' if len(g)>=20 else 'LOW_SUPPORT',**row})
    assert sum(v['n'] for v in children)==len(d)
    for field in ['delta_mse','base_mse','mse']:assert np.isclose(sum(v['n']*v[field] for v in children)/len(d),parent[field],rtol=1e-9,atol=1e-13)
  checks.append({**ident,'rows':len(d),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'status':'PASS'})
 N=pd.DataFrame(nodes);N.to_csv(A/'NESTED_NODES.csv',index=False);pd.DataFrame(cells).to_csv(A/'CELL_RISK.csv.gz',index=False,compression='gzip');pd.DataFrame(routes).to_csv(A/'ROUTING.csv',index=False)
 sensitivity=[];par=N[N.kind=='parent'].set_index(['context','model'])
 for model in ['fixed_guard','causal_selected']:
  for tol in [0.,.01,.05]:
   for kind in ['parent','pulse_band+value_band','segment','segment+pulse_band+value_band']:
    q=N[(N.model==model)&(N.kind==kind)&(N.status=='DESCRIPTIVE')];harm=q[q.q95>(1+tol)*q.base_q95+1e-12]
    hidden=harm[ harm.context.map(lambda c:par.loc[(c,model),'q95']<=(1+tol)*par.loc[(c,model),'base_q95']+1e-12) ]
    sensitivity.append(dict(model=model,tolerance=tol,kind=kind,supported=len(q),harms=len(harm),hidden_harms=len(hidden),hidden_parent_contexts=int(hidden.context.nunique())))
 save('SENSITIVITY.json',sensitivity)
 daily=[]
 for (date,model),g in s.groupby(['date','model']):
  daily.append(dict(date=date,model=model,family=g.family.iloc[0],contexts=len(g),mean_rmse_ratio=float(g.rmse_ratio.mean()),mean_log_rmse_ratio=float(np.log(g.rmse_ratio).mean()),mean_local_harm_fraction=float(g.local_harm_fraction.mean()),active_fraction=float(g.active_n.sum()/g.n.sum()),rmse_improved=int((g.rmse<g.base_rmse-1e-12).sum()),rmse_harmed_1pct=int((g.rmse>1.01*g.base_rmse).sum()),q95_harmed_1pct=int((g.q95>1.01*g.base_q95).sum())))
 save('ACQUISITION_RESULTS.json',daily);D=pd.DataFrame(daily)
 # Paired acquisition bootstrap of observed summaries; descriptive stability, not iid-window inference.
 rng=np.random.default_rng(20261111);dates=sorted(D.date.unique());indices=rng.integers(0,len(dates),size=(10000,len(dates)));boot=[]
 for metric in ['mean_log_rmse_ratio','mean_local_harm_fraction']:
  pivot=D.pivot(index='date',columns='model',values=metric).reindex(dates)
  for comparator in ['history_input','fixed_guard']:
   diff=(pivot.causal_selected-pivot[comparator]).to_numpy();values=diff[indices].mean(axis=1)
   boot.append(dict(metric=metric,comparator=comparator,observed_equal_day_difference=float(diff.mean()),percentile_2_5=float(np.quantile(values,.025)),percentile_97_5=float(np.quantile(values,.975)),resamples=10000,unit='acquisition_date',scope='Descriptive paired resampling stability across observed heterogeneous acquisitions; no window-independence or population-representativeness claim.'))
 save('ACQUISITION_RESAMPLING.json',boot)
 results={}
 for model in ['fixed_guard','causal_selected']:
  q=s[s.model==model];results[model]=dict(contexts=len(q),rmse_improved=int((q.rmse<q.base_rmse-1e-12).sum()),rmse_harm_1pct=int((q.rmse>1.01*q.base_rmse).sum()),q95_harm_1pct=int((q.q95>1.01*q.base_q95).sum()),active_fraction=float(q.active_n.sum()/q.n.sum()),acquisitions_mean_rmse_ratio_lt1=int((D[D.model==model].mean_rmse_ratio<1).sum()))
 results['input_better_than_no_input']=int((s.pivot(index='context',columns='model',values='rmse').history_input<s.pivot(index='context',columns='model',values='rmse').history_no_input).sum())
 results['same_support_windows']=int(s[s.model=='causal_selected'].n.sum());results['acquisitions']=len(dates);results['selected_policy']=json.loads((R/'SELECTED_POLICY.json').read_text())['candidate'];results['sensitivity']=sensitivity
 save('RESULTS.json',results);save('VERIFICATION.json',dict(status='PASS_ATOMIC_METRICS_MATURATION_AND_NESTED_IDENTITIES',contexts=checks,scope='No independent refit; frozen prediction algebra independently reconstructed during execution, policy compared to readable implementation and future masking on actual data.'))
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 rows=D[D.model.isin(['fixed_guard','causal_selected'])].pivot(index='date',columns='model',values='mean_local_harm_fraction').sort_index()
 plt.rcParams.update({'text.color':'#243965','axes.labelcolor':'#243965','xtick.color':'#243965','ytick.color':'#243965','axes.edgecolor':'#ABB4C8'})
 fig,ax=plt.subplots(figsize=(9,6));y=np.arange(len(rows));ax.barh(y+.17,rows.fixed_guard,height=.30,color='#B28CCB',label='Corrección fija protegida');ax.barh(y-.17,rows.causal_selected,height=.30,color='#477CC4',label='Política causal seleccionada');ax.set_yticks(y,rows.index);ax.set_xlabel('Fracción media de jurisdicciones con daño de q95 >1%');ax.set_title('E11 · Transporte local por adquisición');ax.legend(frameon=False);fig.tight_layout();fig.savefig(A/'E11_CARTOGRAFIA.svg');fig.savefig(A/'E11_CARTOGRAFIA.png',dpi=180);plt.close(fig)
 save('ANALYSIS_COMPLETE.json',dict(status='PASS',seconds=time.monotonic()-start,peak_rss_kb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss));print(json.dumps(results),flush=True)
if __name__=='__main__':main()
