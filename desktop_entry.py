"""Standalone exact example: bundled interpreter, persistent report, no package installation."""
from pathlib import Path
import sys,json,runpy,shutil,webbrowser,html,platform
import fractions,itertools,collections,copy,math,time
def main():
 root=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent))
 home=Path(sys.executable).resolve().parent if getattr(sys,'frozen',False) else Path.cwd()
 out=home/'ChronoWitness-results';out.mkdir(exist_ok=True)
 module=runpy.run_path(str(root/'research/design_frontier/tutorial.py'))
 module['main']()
 result=json.loads((root/'research/results/DESIGN_TUTORIAL.json').read_text())
 assert result['status']=='PASS_EXACT_TUTORIAL'
 result['launcher_platform']=platform.platform()
 (out/'EXACT_EXAMPLE.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 page='<!doctype html><html lang="en"><meta charset="utf-8"><title>ChronoWitness result</title><style>body{font:18px/1.6 system-ui;max-width:900px;margin:40px auto;padding:24px;color:#263C68;background:#F7F8FC}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:20px;background:#EDF0FA}a{color:#48458F}</style><h1>ChronoWitness</h1><h2>Exact example verified</h2><p>The two-state identity and certified kinetic contrast were checked using exact rational arithmetic. This example does not evaluate a new cellular experiment.</p><p><a href="https://facundofirmenich.github.io/ChronoWitness/">Explore the evidence graph</a> · <a href="https://github.com/FacundoFirmenich/ChronoWitness">Full reproduction and sources</a></p><pre>'+html.escape(json.dumps(result,indent=2))+'</pre>'
 (out/'RESULT.html').write_text(page,encoding='utf-8')
 print('PASS_STANDALONE_EXACT_EXAMPLE',out)
 if '--no-browser' not in sys.argv:webbrowser.open((out/'RESULT.html').as_uri())
if __name__=='__main__':main()
