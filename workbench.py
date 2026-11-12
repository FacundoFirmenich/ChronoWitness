"""Bilingual entry point for the source and self-contained native distribution."""
import argparse
import html
import json
import locale
import os
from pathlib import Path
import runpy
import subprocess
import sys
import webbrowser

NATIVE=getattr(sys,'frozen',False)
HOME=Path(sys.executable).resolve().parent if NATIVE else Path(__file__).resolve().parent
ROOT=HOME/'source' if NATIVE else HOME
BLOCKS={
 '1':(('Exact reader identities','Identidades exactas de lectores'),['research/reproduce.py']),
 '2':(('Observation and inference','Observación e inferencia'),
      ['research/'+n+'/verify.py' for n in ['finite_reporter','input_robustness','statistical_inference','count_tails','translation_counts','kinetic_reader']]),
 '3':(('Certified design and power','Diseño certificado y potencia'),
      ['research/design_frontier/'+n+'.py' for n in ['certify','power','tutorial','controls']]),
 '4':(('Trajectory assay and application','Ensayo de trayectorias y aplicación'),
      ['research/assay_frontier/run.py','research/application/verify.py']),
}
WORKERS={n for _,scripts in BLOCKS.values() for n in scripts}|{
 'reproduce_release.py','verify_release.py','research/supplement-v08/build_supplement.py',
 'research/assay_frontier/moments.py','research/assay_frontier/calibration.py',
 'research/analysis/verify_phase_python.py','research/analysis/audit_design_structure.py',
 'research/analysis/verify_reader_instrument.py','research/analysis/audit_stochastic.py',
 'research/analysis/audit_markov_boundary.py','research/analysis/verify_markov_boundary.py',
 'research/analysis/audit_general_criterion.py',
}


def worker():
    if not NATIVE or len(sys.argv)<2 or not sys.argv[1].endswith('.py'):
        return False
    path=Path(sys.argv[1]).resolve()
    if not path.is_relative_to(ROOT) or path.relative_to(ROOT).as_posix() not in WORKERS:
        raise SystemExit('Unknown ChronoWitness worker / Programa de cálculo desconocido')
    sys.argv=sys.argv[1:]
    sys.path.insert(0,str(path.parent))
    runpy.run_path(str(path),run_name='__main__')
    return True


def run(script):
    cwd=ROOT/'research' if script.startswith('research/') else ROOT
    subprocess.run([sys.executable,str(ROOT/script)],cwd=cwd,check=True)


def main():
    if worker():
        return
    default='es' if (locale.getlocale()[0] or '').lower().startswith('es') else 'en'
    p=argparse.ArgumentParser(description='ChronoWitness / Reproducción científica')
    p.add_argument('--menu',action='store_true')
    p.add_argument('--lang',choices=['en','es'])
    p.add_argument('--blocks',help='1,2,3,4 / all / atlas / example')
    p.add_argument('--mode',choices=['full','graph','example','doctor'])
    p.add_argument('--no-browser',action='store_true')
    a=p.parse_args()
    language=a.lang or default
    selection=a.blocks or {'full':'all','graph':'atlas','example':'example','doctor':'doctor'}.get(a.mode)
    if selection is None and sys.stdin.isatty():
        print('ChronoWitness · Reproduce / Reproducir')
        print('  all / todo  Complete public core / Núcleo público completo')
        for key,(labels,_) in BLOCKS.items():
            print(f'  {key}  {labels[0]} / {labels[1]}')
        print('  atlas  Evidence atlas / Atlas de evidencia')
        print('  example  Short exact example / Ejemplo exacto breve')
        print('  exit / salir')
        if not NATIVE:
            print('  Source full run uses Docker / La ejecución completa desde fuentes usa Docker')
        tokens=input('Language and choice / Idioma y opción [en 1,3 | es todo]: ').strip().lower().split(maxsplit=1)
        if tokens and tokens[0] in ('en','es'):
            language=tokens.pop(0)
        selection=tokens[0].replace(' ','') if tokens else 'example'
    selection=selection or 'example'
    selection={'todo':'all','salir':'exit'}.get(selection,selection)
    es=language=='es'
    if selection=='exit':
        return
    if selection=='atlas':
        url=(ROOT/'docs/epistemic-graph.html').as_uri()+'?lang='+language
        print(url)
        if not a.no_browser:
            webbrowser.open(url)
        return
    if selection=='doctor':
        print(json.dumps(dict(native=NATIVE,source=str(ROOT),platform=sys.platform),ensure_ascii=False))
        return
    os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
    os.environ.setdefault('OMP_NUM_THREADS','1')
    if NATIVE:
        os.environ['CW_NATIVE_ENGINES']=str(HOME/'engines')
    out=ROOT/'research/results'
    out.mkdir(exist_ok=True)
    before={f.name:(f.stat().st_size,f.stat().st_mtime_ns) for f in out.iterdir() if f.is_file()}
    if selection=='all':
        if NATIVE:
            run('reproduce_release.py')
        else:
            run_args=[sys.executable,str(ROOT/'launch.py'),'--mode','full']
            subprocess.run(run_args,cwd=ROOT,check=True)
    elif selection=='example':
        run('research/design_frontier/tutorial.py')
    else:
        keys=selection.split(',')
        if not keys or any(k not in BLOCKS for k in keys) or len(set(keys))!=len(keys):
            p.error('Seleccioná bloques distintos entre 1 y 4.' if es else 'Choose distinct blocks from 1 to 4.')
        for key in sorted(keys):
            labels,scripts=BLOCKS[key]
            print(labels[int(es)],flush=True)
            for script in scripts:
                run(script)
    fresh=[p.name for p in sorted(out.iterdir()) if p.is_file() and p.suffix in {'.json','.csv','.txt'}
           and p.name!='WORKBENCH_RUN.json' and before.get(p.name)!=(p.stat().st_size,p.stat().st_mtime_ns)]
    record=dict(status='PASS',mode=selection,language=language,native=NATIVE,
                outputs=fresh)
    (out/'WORKBENCH_RUN.json').write_text(json.dumps(record,indent=2),encoding='utf8')
    if sys.stdin.isatty() and not a.no_browser:
        result=out/'RUN.html'
        heading='Cálculo completado' if es else 'Calculation complete'
        links=''.join(f'<li><a href="{html.escape(n,quote=True)}">{html.escape(n)}</a></li>' for n in fresh)
        result.write_text(f'<!doctype html><html lang="{language}"><meta charset="utf-8"><title>ChronoWitness</title>'
                          f'<h1>ChronoWitness · {heading}</h1><p>{html.escape(selection)}</p><ul>{links}</ul>'
                          '<a href="WORKBENCH_RUN.json">JSON</a></html>',encoding='utf8')
        webbrowser.open(result.as_uri())
    print(('Resultados en ' if es else 'Results in ')+str(out))


if __name__=='__main__':
    try:
        main()
    except subprocess.CalledProcessError as e:
        raise SystemExit(e.returncode) from e
