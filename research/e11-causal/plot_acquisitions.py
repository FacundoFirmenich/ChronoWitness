from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path('/content/chronowitness-e11-20261111'); A=R/'analysis'
D=pd.DataFrame(json.loads((A/'ACQUISITION_RESULTS.json').read_text()))
rows=D[D.model.isin(['fixed_guard','causal_selected'])].pivot(index='date',columns='model',values='mean_local_harm_fraction').sort_index()
plt.rcParams.update({'text.color':'#243965','axes.labelcolor':'#243965','xtick.color':'#243965','ytick.color':'#243965','axes.edgecolor':'#ABB4C8'})
fig,ax=plt.subplots(figsize=(9,6));y=np.arange(len(rows))
ax.barh(y+.17,rows.fixed_guard,height=.30,color='#B28CCB',label='Corrección fija protegida')
ax.barh(y-.17,rows.causal_selected,height=.30,color='#477CC4',label='Política causal seleccionada')
ax.set_yticks(y,rows.index);ax.set_xlabel('Fracción media de jurisdicciones con daño de q95 >1%')
ax.set_title('E11 · Transporte local por adquisición');ax.legend(frameon=False);fig.tight_layout()
fig.savefig(A/'E11_CARTOGRAFIA_UTF8.svg',bbox_inches='tight');fig.savefig(A/'E11_CARTOGRAFIA_UTF8.png',dpi=180,bbox_inches='tight');plt.close(fig)
print('ACQUISITION_FIGURE_COMPLETE')
