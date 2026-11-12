"""Exercise both languages, the proof closure and witness in a real browser."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

R=Path(__file__).resolve().parents[1]
CHECK=r'''
<script>
try{
 const assert=(condition,label)=>{if(!condition)throw Error(label);};
 const data=JSON.parse(document.getElementById('ledger').textContent);
 assert(document.getElementById('renderImage').getAttribute('src').startsWith('data:image/svg+xml;base64,'),'offline render preview');
 assert(document.getElementById('openRender').getBoundingClientRect().top<window.innerHeight,'render entry visible');
 assert(document.querySelectorAll('[data-node]').length===15,'initial map');
 document.getElementById('language').click();
 assert(document.documentElement.lang==='es','Spanish toggle');
 assert(document.getElementById('title').textContent==='SuperGraph de ChronoWitness','translated title');
 document.getElementById('lens').children[1].click();
 assert(document.querySelectorAll('[data-node]').length===data.nodes.length,'complete map');
 assert(document.querySelectorAll('[data-edge]').length===data.edges.length,'complete relations');
 document.getElementById('kind').value='source';
 document.getElementById('kind').dispatchEvent(new Event('change'));
 assert(window.CWAtlas.visible().every(id=>id.startsWith('source-')),'source lens');
 const acquisitions=document.getElementById('acquisitions');
 assert(acquisitions.options.length===15,'fourteen reserve dates');
 for(const date of data.acquisitions){
   acquisitions.value=date;acquisitions.dispatchEvent(new Event('change'));
   const node=data.nodes.find(n=>n.date===date);
   assert(document.querySelectorAll('#detail .context').length===node.contexts.length,'local contexts '+date);
 }
 document.getElementById('argument').click();
 window.CWAtlas.select('qualified');
 for(const id of ['fd7','reporter','statistics','qualified'])assert(window.CWAtlas.visible().includes(id),'required premise '+id);
 document.querySelector('[data-level="2"]').click();
 assert(document.getElementById('detail').textContent.includes('SHA-256'),'audit view');
 document.querySelector('[data-edge]').dispatchEvent(new MouseEvent('click',{bubbles:true}));
 assert(document.getElementById('detail').querySelectorAll('button').length===2,'edge inspection');
 for(const route of [...document.getElementById('routes').children]){
   route.click();
   let count=0;
   while(!document.getElementById('next').disabled&&count++<20)document.getElementById('next').click();
   assert(count>0&&count<20,'tour ends');
   document.getElementById('exit').click();
 }
 document.getElementById('witness').click();
 assert(document.querySelectorAll('#graph polyline').length===48,'exact trajectory');
 assert(document.querySelectorAll('#graph circle').length===5,'exact state 3 visits');
 const phase=document.getElementById('phase');phase.value='5';phase.dispatchEvent(new Event('input'));
 assert(document.querySelectorAll('[data-phase-marker]').length===2,'phase inspection');
 assert(document.getElementById('phaseReadout').textContent.includes('5 / 23'),'phase readout');
 phase.value='0';phase.dispatchEvent(new Event('input'));
 assert(document.getElementById('phaseReadout').textContent.includes('0 / 23'),'phase zero');
 phase.value='-1';phase.dispatchEvent(new Event('input'));
 assert(document.querySelectorAll('[data-phase-marker]').length===0,'whole cycle restored');
 const before=document.querySelector('#graph polyline').getAttribute('points');
 document.getElementById('turn').click();
 assert(document.querySelector('#graph polyline').getAttribute('points')!==before,'3D projection');
 document.getElementById('lock').click();
 assert(window.CWAtlas.state().locked,'layout lock');
 assert(JSON.parse(localStorage.getItem('cw-supergraph-v1')).locked,'layout persistence');
 document.body.dataset.qa='pass';
}catch(error){document.body.dataset.qa='fail';document.body.dataset.error=error.message;}
</script>
'''

SUPERGRAPH_CHECK=r'''
<script>
(()=>{
const expected=JSON.parse(document.getElementById('ledger').textContent);
const pass=document.querySelectorAll('[data-node]').length===expected.nodes.length
 &&document.querySelectorAll('[data-edge]').length===expected.edges.length
 &&document.documentElement.lang==='es';
document.body.dataset.qa=pass?'pass':'fail';
})();
</script>
'''

RENDER_CHECK=r'''
<script>
(()=>{
const graph=document.getElementById('graph');
const bounds=graph.getBoundingClientRect();
const checks=[
 [window.CWAtlas?.state().mode==='witness','witness mode'],
 [document.documentElement.lang==='es','Spanish entry'],
 [graph.querySelectorAll('polyline').length===48,'trajectory segments'],
 [graph.querySelectorAll('circle').length===5,'state 3 visits'],
 [bounds.width>0&&bounds.top<window.innerHeight,`visible graph (${bounds.top}, ${window.innerHeight})`],
 [!document.getElementById('phaseControl').hidden,'phase control'],
 [document.getElementById('quickPdf').href.endsWith('FD7_WITNESS_3D_ES.pdf'),'Spanish figure link'],
];
const failed=checks.filter(([pass])=>!pass).map(([,label])=>label);
document.body.dataset.qa=failed.length?'fail':'pass';
if(failed.length)document.body.dataset.error=failed.join(', ');
})();
</script>
'''


def main():
    chrome=os.environ.get('CW_CHROME') or shutil.which('google-chrome') or r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    text=(R/'docs/epistemic-graph.html').read_text(encoding='utf8')
    assert '<script type="application/json" id="ledger">' in text
    with tempfile.TemporaryDirectory(prefix='cw-atlas-') as directory:
        root=Path(directory)
        file=root/'atlas.html'
        file.write_text(text.replace('</html>',CHECK+'</html>'),encoding='utf8')
        render=root/'render-fd7.html'
        render.write_text((R/'docs/render-fd7.html').read_text(encoding='utf8').replace('</html>',RENDER_CHECK+'</html>'),encoding='utf8')
        full=root/'supergraph.html'
        full.write_text((R/'docs/supergraph.html').read_text(encoding='utf8').replace('</html>',SUPERGRAPH_CHECK+'</html>'),encoding='utf8')
        for page,lang in ((file,'en'),(render,'es'),(full,'es')):
            for width in (1440,480):
                run=subprocess.run([chrome,'--headless','--disable-gpu','--disable-background-networking','--no-first-run',
                    '--no-default-browser-check','--user-data-dir='+str(root/f'profile-{page.stem}-{width}'),
                    f'--window-size={width},900','--dump-dom',page.as_uri()+'?lang='+lang],capture_output=True,timeout=45)
                if run.returncode or b'data-qa="pass"' not in run.stdout:
                    hint=[line[:360] for line in run.stdout.splitlines() if b'data-error=' in line][:1]
                    raise RuntimeError(f'Browser check failed at {page.name} {width}: {hint} {run.stderr[-900:]!r}')
    print(json.dumps(dict(status='PASS',viewports=[1440,480],checks=['language','complete map','sources',
      '14 acquisitions','AND closure','edge inspector','guided routes','direct FD7 render','3D rotation','phase inspection','layout persistence'])))


if __name__=='__main__':
    main()
