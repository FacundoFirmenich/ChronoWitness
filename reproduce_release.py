"""Reproduce scientific results, then verify the public distribution."""
from pathlib import Path
import shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent;R=ROOT/'research'
commands=['reproduce.py','finite_reporter/verify.py','input_robustness/verify.py','statistical_inference/verify.py','count_tails/verify.py','translation_counts/verify.py','supplement-v08/build_supplement.py','kinetic_reader/verify.py']
for name in commands:subprocess.run([sys.executable,name],cwd=R,check=True)
shutil.copyfile(R/'design_frontier/SEARCH_RESULT.json',R/'results/DESIGN_SEARCH.json')
for name in ['certify','power','tutorial','controls']:subprocess.run([sys.executable,'design_frontier/'+name+'.py'],cwd=R,check=True)
for name in ['assay_frontier/run.py','application/verify.py']:subprocess.run([sys.executable,name],cwd=R,check=True)
subprocess.run([sys.executable,'verify_release.py'],cwd=ROOT,check=True)
