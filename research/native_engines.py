"""Authenticate the C++ engines shipped in the native reproduction package."""
from pathlib import Path
import hashlib
import json
import os
import platform

ROOT=Path(__file__).resolve().parent


def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()


def resolve(name, configuration=None):
    location=os.environ.get('CW_NATIVE_ENGINES')
    if not location:
        return None
    base=Path(location).resolve()
    receipt=json.loads((base/'ENGINES.json').read_text(encoding='utf8'))
    if (receipt['system'],receipt['machine'])!=(platform.system(),platform.machine()):
        raise RuntimeError('Native engines were built for another platform')
    item=receipt['engines'][name]
    exe=(base/item['file']).resolve()
    if exe.parent!=base or sha(exe)!=item['sha256']:
        raise RuntimeError(f'Invalid native engine: {name}')
    for path,digest in item['source'].items():
        if sha(ROOT/path)!=digest:
            raise RuntimeError(f'Engine source mismatch: {path}')
    if configuration is not None and sha(configuration)!=item['configuration_sha256']:
        raise RuntimeError('Assay configuration mismatch')
    return exe,receipt['compiler']
