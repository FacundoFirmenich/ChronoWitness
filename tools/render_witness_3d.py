"""Render the certified synchronized FD7 witness, not a molecular structure."""
from collections import Counter
from pathlib import Path
import argparse
import json

R=Path(__file__).resolve().parents[1]
PAIR='research/sources/FD7_CERTIFICATE_v0.7.0.json'
WITNESS='expected/core/PHASE_INDEPENDENT_PYTHON.json'


def trace():
    pair=json.loads((R/PAIR).read_bytes())['pair']
    certificate=json.loads((R/WITNESS).read_bytes())
    delta=(0,1,0,2,1,3,2,1)
    states={}
    for arm in 'AB':
        word=pair['sequence_'+arm]
        q=0;path=[q]
        for bit in word:
            q=delta[2*q+int(bit)];path.append(q)
        assert q==0
        counts=Counter(zip(path[:-1],map(int,word)))
        assert [str(counts[s,b]) for s in range(4) for b in range(2)]==certificate['synchronizing_witness_profile_'+arm]
        states[arm]=dict(word=word,path=path,visits=path[:-1].count(3))
    assert [states[x]['visits'] for x in 'AB']==[3,2]
    return dict(arms=states,transition=delta,contrast='1/24',source=WITNESS)


def render(out,lang,formats):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    data=trace()['arms']
    es=lang=='es'
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','svg.hashsalt':'chronowitness-fd7'})
    fig=plt.figure(figsize=(10.4,6.6),facecolor='#f5f3ff')
    ax=fig.add_subplot(projection='3d',computed_zorder=False)
    ax.set_facecolor('#f5f3ff')
    for j,(arm,color) in enumerate((('A','#2168bd'),('B','#8a4fa9'))):
        path=data[arm]['path']
        for k in range(24):
            ax.plot([k,k+1,k+1],[j,j,j],[path[k],path[k],path[k+1]],lw=2.15,color=color,
                    alpha=1 if data[arm]['word'][k]=='1' else .44,zorder=3)
        visits=[k for k,q in enumerate(path[:-1]) if q==3]
        ax.scatter([k+.5 for k in visits],[j]*len(visits),[3]*len(visits),s=65,
                   c='#f5abd7',edgecolors=color,linewidths=1.2,depthshade=False,zorder=4)
    ax.set(xlim=(0,24),ylim=(-.25,1.25),zlim=(0,3.3),xticks=range(0,25,4),yticks=[0,1],zticks=[0,1,2,3])
    ax.set_yticklabels(['FD7-A','FD7-B'])
    ax.set_xlabel('Fase del ciclo' if es else 'Cycle phase',labelpad=9)
    ax.set_zlabel('Estado del lector' if es else 'Reader state',labelpad=8)
    ax.set_box_aspect((3,1,1.15));ax.view_init(elev=24,azim=-67)
    for axis in (ax.xaxis,ax.yaxis,ax.zaxis):
        axis.pane.set_facecolor('#dce6fa');axis.pane.set_alpha(.28)
        axis.label.set_color('#26366e')
    ax.tick_params(colors='#26366e')
    fig.text(.10,.92,'FD7  /  Un ciclo, dos trayectorias' if es else 'FD7  /  One cycle, two trajectories',
             color='#252d60',fontsize=23,weight='semibold')
    fig.text(.10,.872,('Tiempo × brazo × estado del testigo sincronizante' if es else
             'Time × arm × state of the synchronizing witness'),color='#515d90',fontsize=12)
    fig.legend(handles=[Line2D([0],[0],marker='o',linestyle='',color='#8a4fa9',markerfacecolor='#f5abd7',
        label=('Visita al estado 3' if es else 'Visit to state 3')),Line2D([0],[0],color='#2168bd',lw=2,
        label=('Trazo más intenso: entrada 1' if es else 'Stronger trace: input 1'))],
        loc='lower center',bbox_to_anchor=(.5,.10),ncols=2,frameon=False,labelcolor='#26366e')
    fig.text(.5,.058,('Ocupación del estado 3: A = 3/24, B = 2/24. Contraste exacto = 1/24.' if es else
             'State-3 occupation: A = 3/24, B = 2/24. Exact contrast = 1/24.'),ha='center',color='#26366e',fontsize=11)
    fig.subplots_adjust(left=.04,right=.96,bottom=.15,top=.85)
    out.mkdir(parents=True,exist_ok=True)
    for ext in formats:
        metadata={'Date':None} if ext=='svg' else {'CreationDate':None,'ModDate':None} if ext=='pdf' else {}
        fig.savefig(out/f'FD7_WITNESS_3D_{lang.upper()}.{ext}',metadata=metadata,dpi=240)
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,default=R/'docs/assets')
    p.add_argument('--formats',nargs='+',choices=['svg','pdf','png'],default=['svg'])
    args=p.parse_args()
    for language in ('en','es'):
        render(args.output,language,args.formats)
