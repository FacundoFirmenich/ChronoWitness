from pathlib import Path,PurePosixPath
import hashlib,json,os,resource,shutil,subprocess,sys,time,traceback,urllib.request,zipfile
ROOT=Path('/content/chronowitness-e3-20261111')
COMMIT='15f90663027089d4205011f761e5d6151913aed4'
PACKAGE_SHA='9e8848e0449f04ad03f7c08aaf34aee96155580b21fc8b0f11214511556647fc'
DATA_SHA='03a788ddeaa08d3b9ef1511208c8c37263cc5bd55af7e9b41f4f3068ab5ab529'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while c:=f.read(1048576):h.update(c)
    return h.hexdigest()
def fetch(url,p):
    with urllib.request.urlopen(url,timeout=120) as r,p.open('xb') as f:shutil.copyfileobj(r,f,1048576)
def main():
    started=time.monotonic();report=dict(status='RUNNING',source_commit=COMMIT,started_unix=time.time(),cpu_count=os.cpu_count(),meminfo=Path('/proc/meminfo').read_text().splitlines()[:3],stages=[])
    try:
        assert not Path('/dev/nvidia0').exists()
        assert shutil.disk_usage(ROOT).free>2_000_000_000
        fetch(f'https://raw.githubusercontent.com/FacundoFirmenich/ChronoWitness/{COMMIT}/research/e3-calibration-transport/SOURCE_PACKAGE.zip',ROOT/'SOURCE_PACKAGE.zip')
        assert sha(ROOT/'SOURCE_PACKAGE.zip')==PACKAGE_SHA
        with zipfile.ZipFile(ROOT/'SOURCE_PACKAGE.zip') as z:
            assert z.testzip() is None
            for n in z.namelist():
                assert not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts
                (ROOT/n).write_bytes(z.read(n))
        for n,digest in json.loads((ROOT/'SOURCE_MANIFEST.json').read_text()).items():assert sha(ROOT/n)==digest
        t=time.monotonic()
        subprocess.run(['uv','venv','--python','/usr/bin/python3.12',str(ROOT/'venv')],check=True)
        python=str(ROOT/'venv/bin/python')
        subprocess.run(['uv','pip','install','--python',python,'numpy==2.2.6','scipy==1.15.3'],check=True)
        report['stages'].append(dict(stage='environment',seconds=time.monotonic()-t))
        t=time.monotonic();archive=ROOT/'datasets.zip'
        fetch('https://zenodo.org/api/records/8114649/files/datasets.zip/content',archive)
        assert archive.stat().st_size==357636847 and sha(archive)==DATA_SHA
        report['stages'].append(dict(stage='download_verify',seconds=time.monotonic()-t))
        env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
        t=time.monotonic()
        subprocess.run([python,str(ROOT/'e3.py'),str(archive)],cwd=ROOT,env=env,check=True)
        report['stages'].append(dict(stage='E3_science',seconds=time.monotonic()-t))
        report['status']='COMPLETE_E3_COLAB'
    except BaseException:
        report['status']='FAILED';report['error']=traceback.format_exc();raise
    finally:
        report['elapsed_seconds']=time.monotonic()-started
        report['maximum_child_rss_kib']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        (ROOT/'COLAB_RUN.json').write_text(json.dumps(report,indent=2)+'\n')
        files=[p for p in ROOT.rglob('*') if p.is_file() and 'venv' not in p.parts and '__pycache__' not in p.parts and p.name not in ['datasets.zip','execution.log','SHA256.json']]
        manifest={str(p.relative_to(ROOT)):sha(p) for p in files}
        (ROOT/'SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n');files.append(ROOT/'SHA256.json')
        with zipfile.ZipFile(ROOT.with_suffix('.zip'),'x',zipfile.ZIP_DEFLATED) as z:
            for p in files:z.write(p,str(p.relative_to(ROOT)))
        print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
