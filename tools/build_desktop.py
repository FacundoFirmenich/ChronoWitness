"""Build and execute the complete native archive on its target runner."""
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
import sys
import zipfile

R=Path(__file__).resolve().parents[1]
W=R/'research/results/desktop'
W.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R))
from workbench import WORKERS


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    windows=sys.platform=='win32'
    suffix='.exe' if windows else ''
    header_path=W/'assay_config.hpp'
    assay=runpy.run_path(str(R/'research/assay_frontier/run.py'))
    header_path.write_text(assay['configuration'](json.loads((R/'research/assay_frontier/PROTOCOL.json').read_bytes())),
                           encoding='utf8',newline='\n')
    compiler=os.environ.get('CW_CXX','g++')
    compiler_name=subprocess.check_output([compiler,'--version'],text=True).splitlines()[0]
    manifest=json.loads((R/'RELEASE_MANIFEST.json').read_bytes())
    hidden={'scipy.linalg','scipy.stats','scipy.integrate','numpy','cmath','statistics','decimal','fractions','csv'}
    for rel in WORKERS:
        tree=ast.parse((R/rel).read_bytes())
        for node in ast.walk(tree):
            imports=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else []
            hidden.update(n for n in imports if n.split('.')[0] in sys.stdlib_module_names and not n.startswith('_'))
    cmd=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onedir','--name','ChronoWitness',
         '--distpath',str(W/'dist'),'--workpath',str(W/'build'),'--specpath',str(W)]
    for name in sorted(hidden):
        cmd+=['--hidden-import',name]
    subprocess.run([*cmd,str(R/'desktop_entry.py')],check=True,cwd=R)
    package=W/'dist'/'ChronoWitness'
    native=package/'engines'
    native.mkdir(exist_ok=True)
    specs={
        'phase':['analysis/audit_phase_ensemble.cpp'],
        'instrument':['analysis/audit_reader_instrument.cpp','analysis/reader_dynamics.hpp'],
        'assay':['assay_frontier/simulate.cpp','assay_frontier/PROTOCOL.json'],
    }
    engines={}
    for name,sources in specs.items():
        target=native/(name+suffix)
        flags=['-O3','-std=c++17','-ffp-contract=off']
        if windows:
            flags+=['-static']
        if name=='assay':
            flags+=['-I',str(W)]
        subprocess.run([compiler,*flags,str(R/'research'/sources[0]),'-o',str(target)],check=True)
        record=dict(file=target.name,sha256=sha(target),source={p:sha(R/'research'/p) for p in sources})
        if name=='assay':
            record['configuration_sha256']=sha(header_path)
        engines[name]=record
    (native/'ENGINES.json').write_text(json.dumps(dict(system=platform.system(),machine=platform.machine(),
       compiler=compiler_name,engines=engines),indent=2),encoding='utf8')
    source=package/'source'
    for name in sorted(set(manifest['files'])|{'RELEASE_MANIFEST.json'}):
        target=source/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(R/name,target)
    if windows:
        (package/'START_HERE.bat').write_text('@echo off\n"%~dp0ChronoWitness.exe" --menu %*\nif errorlevel 1 pause\n',encoding='utf8')
    else:
        starter=package/('START_HERE.command' if sys.platform=='darwin' else 'START_HERE.sh')
        starter.write_text('#!/bin/sh\nset -eu\ncd -- "$(dirname -- "$0")"\nexec ./ChronoWitness --menu "$@"\n',encoding='utf8',newline='\n')
        starter.chmod(0o755)
    readme=package/'START_HERE.txt'
    readme.write_text('EN: Extract everything and run START_HERE, or the ChronoWitness executable. '
      'One prompt chooses language and the complete public core or selected blocks. No Python, Docker or C++ compiler is needed.\n'
      'ES: Extraé todo y abrí START_HERE o el ejecutable ChronoWitness. Una consulta elige idioma y el núcleo público completo o bloques. '
      'No hace falta instalar Python, Docker ni compilador C++.\n'
      'Unsigned binary / Binario sin firma. Source route / Ruta desde fuentes: source/docs/GETTING_STARTED.md\n',encoding='utf8')
    archive=W/f"ChronoWitness-{platform.system()}-{platform.machine()}.zip"
    # Verify the exact distribution after ZIP extraction, not the build tree.
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(package.rglob('*')):
            if f.is_file():
                z.write(f,f.relative_to(package).as_posix())
    extracted=W/'native-smoke'
    with zipfile.ZipFile(archive) as z:
        z.extractall(extracted)
        if not windows:
            for member in z.infolist():
                if not member.is_dir():
                    (extracted/member.filename).chmod((member.external_attr>>16)&0o777)
    binary=extracted/('ChronoWitness'+suffix)
    subprocess.run([str(binary),'--blocks','2,3','--lang','es','--no-browser'],check=True,cwd=extracted)
    results=extracted/'source/research/results'
    selected=json.loads((results/'WORKBENCH_RUN.json').read_bytes())
    assert selected['mode']=='2,3' and selected['language']=='es'
    subprocess.run([str(binary),'--blocks','all','--lang','en','--no-browser'],check=True,cwd=extracted)
    scientific=json.loads((results/'PUBLIC_VERIFICATION.json').read_bytes())
    assert scientific['status']=='PASS_PUBLIC_CODE_DATA_REPRODUCTION'
    (W/(archive.stem+'.verification.json')).write_text(json.dumps(dict(archive=archive.name,sha256=sha(archive),
       system=platform.system(),machine=platform.machine(),selected=selected,full=scientific),indent=2),encoding='utf8')
    print(archive.name,sha(archive))


if __name__=='__main__':
    main()
