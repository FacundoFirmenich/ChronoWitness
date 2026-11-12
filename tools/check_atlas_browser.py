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
 assert(document.querySelectorAll('[data-node]').length===15,'initial map');
 document.getElementById('language').click();
 assert(document.documentElement.lang==='es','Spanish toggle');
 assert(document.getElementById('title').textContent==='Atlas de evidencia','translated title');
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
 const before=document.querySelector('#graph polyline').getAttribute('points');
 document.getElementById('turn').click();
 assert(document.querySelector('#graph polyline').getAttribute('points')!==before,'3D projection');
 document.getElementById('lock').click();
 assert(window.CWAtlas.state().locked,'layout lock');
 assert(JSON.parse(localStorage.getItem('cw-atlas-v2')).locked,'layout persistence');
 document.body.dataset.qa='pass';
}catch(error){document.body.dataset.qa='fail';document.body.dataset.error=error.message;}
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
        for width in (1440,480):
            run=subprocess.run([chrome,'--headless','--disable-gpu','--disable-background-networking','--no-first-run',
                '--no-default-browser-check','--user-data-dir='+str(root/f'profile-{width}'),f'--window-size={width},900',
                '--dump-dom',file.as_uri()+'?lang=en'],capture_output=True,timeout=45)
            if run.returncode or b'data-qa="pass"' not in run.stdout:
                hint=[line for line in run.stdout.splitlines() if b'data-error=' in line][:1]
                raise RuntimeError(f'Browser check failed at {width}: {hint} {run.stderr[-900:]!r}')
    print(json.dumps(dict(status='PASS',viewports=[1440,480],checks=['language','AND closure','edge inspector','guided routes','FD7 trajectories','3D rotation','layout persistence'])))


if __name__=='__main__':
    main()
