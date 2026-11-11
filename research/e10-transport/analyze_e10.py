"""Atomic verification, exact risk decomposition and nested diagnostics; MIT."""
from pathlib import Path
import json,time,hashlib,zipfile,resource
import numpy as np,pandas as pd
R=Path('/content/chronowitness-e10-20261111');O=R/'evaluation';A=R/'analysis';A.mkdir(exist_ok=True)
def save(n,x):(A/n).write_text(json.dumps(x,indent=2,allow_nan=False))
def score(g,ident,kind,labels):
 e=g.history_input_error.to_numpy();c=g.applied_c.to_numpy();v=g.local_guarded_error.to_numpy()
 delta=float(np.mean(v*v-e*e));formula=float(np.mean(c*c-2*c*e))
 assert np.isclose(delta,formula,rtol=1e-9,atol=1e-13)
 b=float(np.quantile(abs(e),.95));q=float(np.quantile(abs(v),.95));m=float(np.mean(e*e));gm=float(np.mean(v*v))
 return {**ident,'kind':kind,'labels':json.dumps(labels),'n':len(g),'cells':int(g.track.nunique()),'status':'DESCRIPTIVE' if len(g)>=20 else 'LOW_SUPPORT','base_mse':m,'guard_mse':gm,'delta_mse':delta,'identity_delta':formula,'q95_base':b,'q95_guard':q,'q95_ratio':q/b if b>0 else None,'rmse_ratio':float(np.sqrt(gm/m)) if m>0 else None}
def main():
 start=time.monotonic();summary=pd.DataFrame(json.loads((R/'SUMMARY.json').read_text()));cells=[];nodes=[];verified=[];contexts=[]
 for f in sorted(O.glob('*_residuals.csv.gz')):
  d=pd.read_csv(f);stem=f.name.removesuffix('_residuals.csv.gz');h=int(stem.split('_h')[-1].split('_')[0]);align=int(stem.split('_a')[-1]);name=stem.split('_h')[0]+'.csv'
  identrow=summary[(summary.file==name)&(summary.horizon==h)&(summary.alignment==align)].iloc[0]
  ident={k:identrow[k].item() if hasattr(identrow[k],'item') else identrow[k] for k in ['file','date','clock','horizon','alignment']};ident['context']=stem
  dd=json.loads((O/(stem+'_decisions.json')).read_text());lookup={x['track']:x for x in dd}
  if d.empty:
   verified.append({**ident,'status':'NOT_ESTIMABLE','n':0});continue
  assert d.stage.eq('late').all() and not d.duplicated(['track','origin']).any()
  c=d.track.map(lambda t:lookup[t]['correction']).to_numpy();accepted=d.track.map(lambda t:lookup[t]['accepted']).to_numpy(dtype=bool)
  assert np.allclose(d.persistence_error,d.y-d.target,rtol=0,atol=1e-12)
  assert np.allclose(d.local_unguarded_error,d.history_input_error-c,rtol=0,atol=1e-12)
  assert np.allclose(d.local_guarded_error,d.history_input_error-c*accepted,rtol=0,atol=1e-12)
  for decision in dd:
   b=decision['validation_before'];a=decision['validation_after']
   reconstructed=decision['early_n']>=5 and decision['validation_n']>=3 and a['rmse']<b['rmse'] and a['q95']<=1.01*b['q95']
   assert decision['accepted']==reconstructed
  for model in ['persistence','history_no_input','history_input','local_unguarded','local_guarded']:
   r=summary[(summary.file==name)&(summary.horizon==h)&(summary.alignment==align)&(summary.model==model)].iloc[0];v=d[model+'_error'].to_numpy()
   assert len(v)==r['n']
   for actual,expected in [(np.sqrt(np.mean(v*v)),r.rmse),(np.mean(abs(v)),r.mae),(np.mean(v),r.bias),(np.quantile(abs(v),.95),r.q95)]:assert abs(actual-expected)<1e-12
  d['applied_c']=c*accepted
  # Three equal-duration intervals of late origin times; never split by outcomes.
  first=int(d.origin.min());last=int(d.origin.max());d['late_segment']=np.minimum(2,((d.origin-first)*3//(last-first+1))).astype(int)
  parent=score(d,ident,'parent',{});contexts.append(parent);nodes.append(parent)
  for dims in [['pulse_band','value_band'],['late_segment'],['late_segment','pulse_band','value_band']]:
   children=[]
   for key,g in d.groupby(dims,observed=True):
    if not isinstance(key,tuple):key=(key,)
    labels={k:(v.item() if hasattr(v,'item') else v) for k,v in zip(dims,key)}
    row=score(g,ident,'+'.join(dims),labels);nodes.append(row);children.append(row)
   assert sum(x['n'] for x in children)==len(d)
   for field in ['delta_mse','base_mse','guard_mse']:
    reconstructed=sum(x['n']*x[field] for x in children)/len(d)
    assert np.isclose(reconstructed,parent[field],rtol=1e-9,atol=1e-13)
  for tid,g in d.groupby('track'):
   dec=lookup[tid];e=g.history_input_error.to_numpy();mu=float(np.mean(e));c0=dec['correction'];active=bool(dec['accepted']);ca=c0 if active else 0.
   delta=float(np.mean(g.local_guarded_error**2-e**2));formula=ca*ca-2*ca*mu
   assert np.isclose(delta,formula,rtol=1e-9,atol=1e-13)
   mode='ABSTAIN' if not active or ca==0 else 'SIGN_REVERSAL' if ca*mu<=0 else 'OVERSHOOT' if abs(ca)>2*abs(mu) else 'NONHARMFUL'
   if active and ca!=0:assert (formula>0)==(mode in ['SIGN_REVERSAL','OVERSHOOT'])
   cells.append({**ident,'track':int(tid),'n':len(g),'early_n':dec['early_n'],'validation_n':dec['validation_n'],'accepted':active,'correction':c0,'late_mean_error':mu,'delta_mse':delta,'identity_delta':formula,'mode':mode,'status':'DESCRIPTIVE' if len(g)>=20 else 'LOW_SUPPORT'})
  verified.append({**ident,'status':'PASS','n':len(d),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 save('VERIFICATION.json',{'status':'PASS_ATOMIC_METRICS_DECISIONS_NESTED_CONSERVATION','files':verified,'does_not_independently_refit_or_validate_biology':True})
 C=pd.DataFrame(cells);N=pd.DataFrame(nodes);T=pd.DataFrame(contexts)
 C.to_csv(A/'CELL_RISK_DECOMPOSITION.csv.gz',index=False,compression='gzip');N.to_csv(A/'NESTED_NODES.csv',index=False);T.to_csv(A/'CONTEXTS.csv',index=False)
 ix=['file','date','clock','horizon','alignment'];q=summary.pivot(index=ix,columns='model',values='q95');r=summary.pivot(index=ix,columns='model',values='rmse')
 comparisons=[]
 for key,group in summary.groupby(['date','clock','horizon','alignment']):
  qq=group.pivot(index='file',columns='model',values='q95');rr=group.pivot(index='file',columns='model',values='rmse')
  comparisons.append(dict(date=key[0],clock=int(key[1]),horizon=int(key[2]),alignment=int(key[3]),contexts=len(qq),guard_q95_harm_1pct=int((qq.local_guarded>1.01*qq.history_input).sum()),guard_rmse_harm_1pct=int((rr.local_guarded>1.01*rr.history_input).sum()),input_better=int((rr.history_input<rr.history_no_input).sum()),guard_better=int((rr.local_guarded<rr.history_input-1e-12).sum())))
 save('STRATIFIED_COMPARISONS.json',comparisons)
 sensitivity=[]
 for tol in [0.,.01,.05]:
  # A numerical tolerance at exact equality avoids counting serialization roundoff.
  for kind in ['parent','pulse_band+value_band','late_segment','late_segment+pulse_band+value_band']:
   sel=N[(N.kind==kind)&(N.status=='DESCRIPTIVE')];harms=sel[sel.q95_guard>(1+tol)*sel.q95_base+1e-12]
   par=T.set_index('context');hidden=harms[harms.context.map(lambda k:par.loc[k,'q95_guard']<=(1+tol)*par.loc[k,'q95_base']+1e-12)]
   sensitivity.append(dict(tolerance=tol,kind=kind,supported=len(sel),q95_harms=len(harms),harms_in_unflagged_parents=len(hidden),distinct_unflagged_parents=int(hidden.context.nunique())))
 save('THRESHOLD_SENSITIVITY.json',sensitivity)
 bymode=[]
 for key,g in C.groupby(['date','mode']):bymode.append(dict(date=key[0],mode=key[1],cell_contexts=len(g),windows=int(g.n.sum()),sum_squared_error_change=float((g.n*g.delta_mse).sum())))
 save('RISK_MODES.json',bymode)
 active=C[C.accepted&(C.correction!=0)];harm=active[active['mode'].isin(['SIGN_REVERSAL','OVERSHOOT'])]
 out=dict(contexts=len(q),input_better=int((r.history_input<r.history_no_input).sum()),guard_better=int((r.local_guarded<r.history_input-1e-12).sum()),guard_rmse_harm_1pct=int((r.local_guarded>1.01*r.history_input).sum()),unguarded_rmse_harm_1pct=int((r.local_unguarded>1.01*r.history_input).sum()),guard_q95_harm_1pct=int((q.local_guarded>1.01*q.history_input).sum()),unguarded_q95_harm_1pct=int((q.local_unguarded>1.01*q.history_input).sum()),cell_contexts=len(C),active_cell_contexts=len(active),harmful_active_cell_contexts=len(harm),harm_modes={k:int(v) for k,v in harm['mode'].value_counts().items()},worst_supported_local_q95_ratio=float(N[(N.kind=='pulse_band+value_band')&(N.status=='DESCRIPTIVE')].q95_ratio.max()),threshold_sensitivity=sensitivity,seconds=time.monotonic()-start)
 save('RESULTS.json',out)
 # Scientific export palette: blue/purple/rose, no graphical black/red/green/yellow.
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.colors import LinearSegmentedColormap
 plt.rcParams.update({'text.color':'#243965','axes.labelcolor':'#243965','xtick.color':'#243965','ytick.color':'#243965','axes.edgecolor':'#9DA9BE','font.size':10})
 grouped=pd.DataFrame(comparisons);matrix=grouped.groupby(['clock','horizon']).agg(harms=('guard_q95_harm_1pct','sum'),total=('contexts','sum'));v=(matrix.harms/matrix.total).unstack().reindex([5,7,20,30])
 fig,ax=plt.subplots(figsize=(7.4,4.4));im=ax.imshow(v.to_numpy(),vmin=0,vmax=1,cmap=LinearSegmentedColormap.from_list('cw',['#F4F2FB','#A4B6E8','#7761B2','#CF8CB5']))
 for i,clock in enumerate(v.index):
  for j,h in enumerate(v.columns):a=matrix.loc[(clock,h)];ax.text(j,i,f'{int(a.harms)}/{int(a.total)}',ha='center',va='center',color='#243965')
 ax.set_xticks(range(len(v.columns)),[str(x) for x in v.columns]);ax.set_yticks(range(len(v.index)),[str(x) for x in v.index]);ax.set_xlabel('Horizonte de predicción (min)');ax.set_ylabel('Reloj de estímulo (min)');ax.set_title('E10 · daño de q95 >1% con protección local');fig.colorbar(im,ax=ax,label='Fracción de contextos');fig.text(.1,.015,'Ambos alineamientos incluidos; los contextos no son réplicas independientes.',fontsize=8);fig.tight_layout(rect=[0,.04,1,1]);fig.savefig(A/'E10_MAPA_TRANSPORTE.svg');fig.savefig(A/'E10_MAPA_TRANSPORTE.png',dpi=180);plt.close(fig)
 (R/'ANALYSIS_COMPLETE.json').write_text(json.dumps({'status':'PASS','seconds':time.monotonic()-start,'peak_rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
 print(json.dumps(out),flush=True)
if __name__=='__main__':main()
