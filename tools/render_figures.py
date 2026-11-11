"""Render exact input structure and observed acquisition-level evidence; no fitted or invented data."""
from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from matplotlib.ticker import PercentFormatter,MaxNLocator
R=Path(__file__).resolve().parents[1];O=R/'research/results/figures';O.mkdir(parents=True,exist_ok=True)
blue='#356FA8';indigo='#48458F';pink='#B94C8C';pale='#EDF0FA';ink='#263C68'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'text.color':ink,'axes.labelcolor':ink,'axes.edgecolor':ink,'xtick.color':ink,'ytick.color':ink,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'})
def save(fig,name):
 for ext in ['pdf','svg','png']:fig.savefig(O/(name+'.'+ext),bbox_inches='tight',dpi=400)
 plt.close(fig)
pair=json.loads((R/'research/sources/FD7_CERTIFICATE_v0.7.0.json').read_text())['pair'];a=pair['sequence_A'];b=pair['sequence_B']
def counts(w,k):return Counter(''.join(w[(i+j)%len(w)] for j in range(k)) for i in range(len(w)))
diff=[]
for k in range(1,9):
 ca,cb=counts(a,k),counts(b,k);diff.append(sum(abs(ca[x]-cb[x]) for x in ca.keys()|cb.keys()))
assert diff==[0]*7+[8]
fig,axs=plt.subplots(2,1,figsize=(11,6),layout='constrained',gridspec_kw={'height_ratios':[1,2]})
axs[0].imshow([[int(z) for z in a],[int(z) for z in b]],cmap=matplotlib.colors.ListedColormap([pale,blue]),aspect='auto');axs[0].set_yticks([0,1],['FD7 A','FD7 B']);axs[0].set_xticks(range(0,24,2),range(1,25,2));axs[0].set_xlabel('Pulse position');axs[0].set_title('A  Identical low-order summaries, distinct temporal order',loc='left')
axs[1].bar(range(1,9),diff,color=[blue]*7+[pink]);axs[1].scatter(range(1,8),[0]*7,color=indigo,zorder=3);axs[1].set_xticks(range(1,9));axs[1].set_xlabel('Cyclic word length');axs[1].set_ylabel('L1 difference of counts');axs[1].yaxis.set_major_locator(MaxNLocator(integer=True));axs[1].set_title('B  First difference at order eight',loc='left');save(fig,'FD7_EXACT_STRUCTURE')
rows=json.loads((R/'research/e11-causal/RESERVE_SUMMARY.json').read_text());groups=defaultdict(list)
for r in rows:
 if r['model'] in ['fixed_guard','causal_selected']:groups[r['date'],r['model']].append(r['local_harm_fraction'])
dates=sorted({d for d,m in groups});assert len(dates)==14
fig,ax=plt.subplots(figsize=(10,8),layout='constrained')
for off,model,col,label in [(-.17,'fixed_guard',indigo,'Fixed guard'),(.17,'causal_selected',pink,'Selected causal policy')]:
 vals=[sum(groups[d,model])/len(groups[d,model]) for d in dates];ax.barh([i+off for i in range(len(dates))],vals,height=.28,color=col,label=label)
ax.set_yticks(range(len(dates)),dates);ax.xaxis.set_major_formatter(PercentFormatter(1));ax.set_xlabel('Mean fraction of supported local nodes with q95 harm >1%');ax.set_title('E11 · Retain the acquisition, expose the local tail',loc='left',pad=16);ax.legend(frameon=False);fig.text(.15,-.02,'Context averages within acquisition; overlapping nodes are not independent replicates.',fontsize=9);save(fig,'E11_LOCAL_TAILS')
for lang in ['ES','EN']:
 es=lang=='ES';fig,ax=plt.subplots(figsize=(12,5));ax.set_xlim(0,12);ax.set_ylim(0,5);ax.axis('off')
 ax.text(.2,4.65,'ChronoWitness',fontsize=27,fontweight='bold',color=indigo)
 ax.text(.2,4.14,'De la identidad temporal a la evidencia local' if es else 'From temporal identity to local evidence',fontsize=16)
 labels=['Diseñar\nentradas equivalentes','Derivar\nidentidades exactas','Medir\ncon presupuesto de error','Decidir\npor jurisdicción'] if es else ['Design\nmatched inputs','Derive\nexact identities','Measure\nwith an error budget','Decide\nwithin jurisdictions']
 for i,label in enumerate(labels):
  x=.2+3*i;ax.add_patch(FancyBboxPatch((x,2.25),2.5,1.05,boxstyle='round,pad=0.1',facecolor=pale,edgecolor=blue if i<3 else pink,lw=1.5));ax.text(x+1.25,2.78,label,ha='center',va='center',fontsize=12)
  if i<3:ax.add_patch(FancyArrowPatch((x+2.65,2.78),(x+2.9,2.78),arrowstyle='-|>',mutation_scale=15,color=indigo))
 ax.text(.2,1.45,'Teoría: FD7/FD8 y modelos lectores' if es else 'Theory: FD7/FD8 and reader models',fontsize=13,color=blue)
 ax.text(.2,.96,'Datos celulares: transporte y calibración bajo otros estímulos' if es else 'Cellular data: transport and calibration under other stimuli',fontsize=13,color=pink)
 ax.text(.2,.35,'Conservar soporte, intersecciones, colas, daños y abstenciones.' if es else 'Retain support, intersections, tails, harms and abstentions.',fontsize=11)
 save(fig,'VISUAL_ABSTRACT_'+lang)
sources=['research/sources/FD7_CERTIFICATE_v0.7.0.json','research/e11-causal/RESERVE_SUMMARY.json','tools/render_figures.py']
(O/'PROVENANCE.json').write_text(json.dumps({'sources':{p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in sources},'outputs':sorted(p.name for p in O.iterdir() if p.suffix in ['.pdf','.svg','.png']),'dpi':400,'numeric_data_modified':False},indent=2))
print('PASS exact structure, 14 acquisition rows and bilingual abstract rendered')
