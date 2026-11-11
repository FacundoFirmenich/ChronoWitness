"""Post-evaluation descriptive local map; no changes to model, policy or scores."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm,LinearSegmentedColormap
R=Path('/content/chronowitness-e11-20261111');A=R/'analysis'
d=pd.read_csv(A/'NESTED_NODES.csv');q=d[(d.model=='causal_selected')&(d.kind=='pulse_band+value_band')&(d.status=='DESCRIPTIVE')]
worst=q.loc[q.q95_ratio.idxmax()];context=worst.context
subset=d[(d.context==context)&(d.model=='causal_selected')]
parent=subset[subset.kind=='parent'].iloc[0]
grids=[];counts=[]
for segment in [None,0,1,2]:
 g=subset[subset.kind==('pulse_band+value_band' if segment is None else 'segment+pulse_band+value_band')]
 values=np.full((4,3),np.nan);support=np.zeros((4,3),dtype=int)
 for _,r in g.iterrows():
  label=json.loads(r.labels)
  if segment is not None and label['segment']!=segment:continue
  i=label['pulse_band']+1;j=label['value_band'];values[i,j]=r.q95_ratio;support[i,j]=int(r.n)
 grids.append(values);counts.append(support)
finite=np.concatenate([a[np.isfinite(a)] for a in grids]);span=max(.02,float(np.max(abs(finite-1))))
cmap=LinearSegmentedColormap.from_list('cwlocal',['#547FCC','#F5F3FA','#CA8CB4']);cmap.set_bad('#ECEFF5')
plt.rcParams.update({'text.color':'#243965','axes.labelcolor':'#243965','xtick.color':'#243965','ytick.color':'#243965','axes.edgecolor':'#ABB4C8'})
fig,axes=plt.subplots(1,4,figsize=(15,4.6),sharey=True)
for k,(ax,v,n) in enumerate(zip(axes,grids,counts)):
 im=ax.imshow(v,cmap=cmap,norm=TwoSlopeNorm(vmin=1-span,vcenter=1,vmax=1+span),aspect='auto')
 for i in range(4):
  for j in range(3):
   label='sin soporte' if not np.isfinite(v[i,j]) else f'{v[i,j]:.3f}\nn={n[i,j]}'+ ('\nLOW' if n[i,j]<20 else '')
   ax.text(j,i,label,ha='center',va='center',fontsize=8,color='#243965')
 ax.set_title('Intervalo tardío completo' if k==0 else f'Segmento tardío {k}');ax.set_xticks([0,1,2],['baja','media','alta']);ax.set_xlabel('Banda de señal (TRAIN)');ax.set_yticks(range(4),['sin pulso previo','0–4 min','5–14 min','≥15 min'])
axes[0].set_ylabel('Tiempo desde el último pulso')
fig.suptitle(f'E11 · Jurisdicción adversa conservada · {worst.date} · h={int(worst.horizon)} · alineamiento={int(worst.alignment)}',fontsize=13)
fig.text(.06,.015,f'Caso elegido retrospectivamente por máximo q95 local/base. Padre: razón={parent.q95_ratio:.3f}. Las celdas muestran q95 causal/base; no son réplicas.',fontsize=9)
fig.subplots_adjust(left=.09,right=.90,bottom=.18,top=.84,wspace=.18);cax=fig.add_axes([.92,.23,.013,.54]);fig.colorbar(im,cax=cax,label='Razón de q95')
fig.savefig(A/'E11_JURISDICCION_LOCAL.svg',bbox_inches='tight');fig.savefig(A/'E11_JURISDICCION_LOCAL.png',dpi=180,bbox_inches='tight');plt.close(fig)
(A/'LOCAL_CASE_SELECTION.json').write_text(json.dumps(dict(scope='Post-evaluation descriptive adverse-case selection; not a new test or a representative case',criterion='Maximum causal/base q95 ratio among supported pulse-band x TRAIN-value-band nodes',context=context,ratio=float(worst.q95_ratio),parent_ratio=float(parent.q95_ratio),labels=json.loads(worst.labels),n=int(worst.n)),indent=2))
print('LOCAL_CASE',context,float(worst.q95_ratio))
