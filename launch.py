"""Portable entry point. No administrator privileges or silent installers."""
from pathlib import Path
import argparse,json,platform,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser(description="ChronoWitness: exact example, reproducibility and evidence")
 p.add_argument('--mode',choices=['example','doctor','full','graph'],default='example')
 a=p.parse_args()
 if a.mode=='doctor':
  print(json.dumps(dict(python=platform.python_version(),system=platform.system(),machine=platform.machine(),docker=shutil.which('docker'),compiler=shutil.which('g++'),example_requires='Python 3.12 recommended; standard library only',full_requires='Docker Engine running; internet for first build'),indent=2));return
 if a.mode=='graph':
  import webbrowser
  webbrowser.open((ROOT/'docs/epistemic-graph.html').as_uri());return
 if a.mode=='example':
  subprocess.run([sys.executable,str(ROOT/'research/design_frontier/tutorial.py')],cwd=ROOT,check=True)
  print('Result: '+str(ROOT/'research/results/DESIGN_TUTORIAL.json'));return
 if not shutil.which('docker'):p.error('Install and start Docker Desktop (Windows/macOS) or Docker Engine (Linux), then rerun --mode full. See docs/GETTING_STARTED.md.')
 subprocess.run(['docker','info'],stdout=subprocess.DEVNULL,check=True)
 image='chronowitness:0.14.3'
 subprocess.run(['docker','build','--platform','linux/amd64','-t',image,str(ROOT)],check=True)
 out=ROOT/'research/results';out.mkdir(parents=True,exist_ok=True)
 subprocess.run(['docker','run','--rm','--platform','linux/amd64','--mount',f'type=bind,source={out},target=/work/research/results',image],check=True)
 print('Verified outputs: '+str(out))
if __name__=='__main__':
 try:main()
 except subprocess.CalledProcessError as e:sys.exit(e.returncode)
