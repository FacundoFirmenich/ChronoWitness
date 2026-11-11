"""Regenerate the offline graph and bind each claim to current source bytes."""
from pathlib import Path
import json,hashlib,argparse
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
data=json.loads((R/'docs/EVIDENCE_LEDGER.json').read_text(encoding='utf-8'))
ids={x['id'] for x in data['nodes']};assert len(ids)==len(data['nodes'])
for n in data['nodes']:
 source=R/n['source'];assert source.is_file(),source
 n['sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
for e in data['edges']:assert e['from'] in ids and e['to'] in ids
template=(R/'tools/graph-template.html').read_text(encoding='utf-8')
html=template.replace('__LEDGER__',json.dumps(data,ensure_ascii=False).replace('</',r'<\/'))
out=R/'docs/epistemic-graph.html'
if a.check:assert out.read_text(encoding='utf-8')==html,'Graph stale: run python tools/build_evidence.py'
else:out.write_text(html,encoding='utf-8',newline='\n')
print('PASS evidence sources, relations and generated graph')
