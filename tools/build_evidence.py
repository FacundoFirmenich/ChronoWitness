"""Regenerate the offline graph and bind each claim to current source bytes."""
from pathlib import Path
import json,hashlib,argparse,base64
from render_witness_3d import trace
from supergraph_model import extend
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
data=json.loads((R/'docs/EVIDENCE_LEDGER.json').read_text(encoding='utf-8'))
translations={
 'fd7':('Identidad de entrada FD7','Los conteos cíclicos coinciden hasta orden siete; la identidad de ocupación tiene una clase declarada.','formal'),
 'reader':('Umbrales de lectores','Los umbrales se refieren a las clases de lectores y observables definidos.','formal'),
 'kinetic':('Separación cinética','El certificado establece existencia y contraste para un testigo; no declara un óptimo global.','formal'),
 'reporter':('Reportero y adquisición','La cascada lineal estable es común; las ventanas finitas requieren control de extremos o transitorios.','assay'),
 'statistics':('Inferencia secuencial','La validez depende del soporte acotado y del presupuesto condicional de sesgo.','assay'),
 'e4':('Calibración local E4','La selección temprana se evalúa por segmento y banda de señal, conservando las pérdidas de cola.','observed'),
 'e8':('Transporte anidado E6–E8','El resultado distingue jurisdicciones anidadas y conserva los casos adversos.','observed'),
 'e9':('Predicción temporal congelada E9','El protocolo y los coeficientes de predicción se fijan antes de la evaluación.','observed'),
 'e10':('Transporte entre adquisiciones E10','Las adquisiciones adicionales contrastan la política con modelos congelados.','observed'),
 'e11':('Adquisiciones reservadas E11','Una política causal local se eligió antes de evaluar catorce adquisiciones reservadas.','observed'),
 'harm':('Ausencia uniforme de deterioro local','Se conservan 6/756 y 81/2.268 jurisdicciones que exceden el 1 % de deterioro de q95.','limits'),
 'physical':('Comparación celular emparejada FD7/FD8','Los registros E11 responden a programas de entrada publicados; la comparación celular directa no fue evaluada.','limits'),
 'date':('Fecha de adquisición en conflicto','El registro se excluyó de la evaluación reservada y su procedencia permanece visible.','limits'),
 'witness':('Testigo sincronizante de cuatro estados','El estado 3 aparece 3/24 veces en el brazo A y 2/24 en B. Contraste exacto: 1/24.','formal'),
 'qualified':('Interpretación del contraste observado','El contraste requiere conjuntamente la identidad del modelo, un modelo de observación cualificado y un contrato de inferencia válido.','assay'),
}
data['nodes'] += [
 dict(id='witness',title='Synchronizing four-state witness',status='EXACT',source='expected/core/PHASE_INDEPENDENT_PYTHON.json',
      meaning='State 3 is visited 3/24 times under arm A and 2/24 under arm B. Exact contrast: 1/24.'),
 dict(id='qualified',title='Interpretation of an observed contrast',status='CONDITIONAL',source='docs/ASSAY_GUIDE.md',
      meaning='Interpretation requires the model identity, a qualified observation model and a valid inference contract together.',
      premises=['fd7','reporter','statistics']),
]
data['edges'] += [
 dict(**{'from':'reader','to':'witness'},relation='exhibits a separating witness'),
 *[dict(**{'from':p,'to':'qualified'},relation='required premise') for p in ('fd7','reporter','statistics')]
]
relations=['restringe','admite un testigo separador','se conserva bajo hipótesis','aporta el presupuesto de sesgo',
 'amplía el análisis','motiva la validación temporal','transporta el modelo congelado','el desarrollo precede a la reserva',
 'conserva evidencia adversa','queda fuera de esta evaluación','excluye un registro en conflicto',
 'exhibe un testigo separador','premisa necesaria','premisa necesaria','premisa necesaria']
assert len(relations)==len(data['edges'])
for i,(edge,es) in enumerate(zip(data['edges'],relations)):
 edge.update(id='edge-'+str(i),relation_es=es)
for node in data['nodes']:
 node['title_es'],node['meaning_es'],node['group']=translations[node['id']]
extend(data)
data['schema_version']=2
data['updated']='2026-11-12'
data['witness']=trace()
data['local_case']=json.loads((R/'research/e11-causal/LOCAL_CASE_SELECTION.json').read_bytes())
ids={x['id'] for x in data['nodes']};assert len(ids)==len(data['nodes'])
for n in data['nodes']:
 source=R/n['source'];assert source.is_file(),source
 n['sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
for e in data['edges']:assert e['from'] in ids and e['to'] in ids
assert len({e['id'] for e in data['edges']})==len(data['edges'])
for node in data['nodes']:
 if node['kind']=='gate':
  assert set(node['premises'])=={e['from'] for e in data['edges'] if e['to']==node['id'] and e['kind']=='premise'}
assert all(set(route['steps'])<=ids for route in data['routes'])
assert all(sum(e['to']==n['id'] and e['kind']=='provenance' for e in data['edges'])==1
           for n in data['nodes'] if n['kind']!='source')
template=(R/'tools/graph-template.html').read_text(encoding='utf-8')
script=(R/'tools/spatial_atlas.js').read_text(encoding='utf8')
data['render_previews']={lang:'data:image/svg+xml;base64,'+base64.b64encode(
    (R/f'docs/assets/FD7_WITNESS_3D_{lang.upper()}.svg').read_bytes()).decode() for lang in ('en','es')}
html=template.replace('__LEDGER__',json.dumps(data,ensure_ascii=False).replace('</',r'<\/')).replace('__SCRIPT__',script)
screens={'index.html':'map','epistemic-graph.html':'map','supergraph.html':'supergraph','render-fd7.html':'render'}
outputs={R/'docs'/name:html.replace('__SCREEN__',screen) for name,screen in screens.items()}
data.pop('render_previews')
outputs[R/'docs/ATLAS_LEDGER.json']=json.dumps(data,indent=2,ensure_ascii=False)+'\n'
for path,content in outputs.items():
 if a.check:assert path.read_text(encoding='utf-8')==content,'Graph stale: '+str(path)
 else:path.write_text(content,encoding='utf-8',newline='\n')
print('PASS evidence sources, relations and generated graph')
