from pathlib import Path
import subprocess,sys,zipfile,shutil,json,hashlib,platform
R=Path(__file__).resolve().parents[1];W=R/'research/results/desktop';W.mkdir(parents=True,exist_ok=True)
data=W/'bundle'
files=['research/design_frontier/tutorial.py','research/analysis/verify_markov_boundary.py','research/analysis/audit_stochastic.py','research/supplement-v011/data/Data_S12_design_certificate.json']
for name in files:
 p=data/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/name,p)
cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onefile','--name','ChronoWitness','--distpath',str(W/'dist'),'--workpath',str(W/'build'),'--specpath',str(W),'--add-data',str(data/'research')+':research',str(R/'desktop_entry.py')]
subprocess.run(cmd,check=True,cwd=R)
binary=W/'dist'/('ChronoWitness.exe' if sys.platform=='win32' else 'ChronoWitness')
subprocess.run([str(binary),'--no-browser'],check=True,cwd=W)
receipt=json.loads((binary.parent/'ChronoWitness-results/EXACT_EXAMPLE.json').read_text());assert receipt['status']=='PASS_EXACT_TUTORIAL'
name='ChronoWitness-'+platform.system()+'-'+platform.machine()+'.zip';out=W/name
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 z.write(binary,binary.name);z.write(R/'LICENSE','LICENSE');z.writestr('START_HERE.txt','Extract the ZIP. Run ChronoWitness (Windows: ChronoWitness.exe). No Python installation is needed. The exact example writes ChronoWitness-results/RESULT.html and opens it in your browser. The full scientific campaign remains a separate Docker/source route. This binary is unsigned; do not disable system security. If your system blocks it, use the documented Python source route.\n');z.writestr('BUILD_VERIFICATION.json',json.dumps(receipt,indent=2))
print(name,hashlib.sha256(out.read_bytes()).hexdigest())
