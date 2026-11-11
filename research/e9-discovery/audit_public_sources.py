"""Bounded public-data audit. Inspects identities and inputs, not response scores."""
import collections
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent

class RangeFile(io.RawIOBase):
    def __init__(self, url, size, budget=32_000_000):
        self.url, self.size, self.budget = url, size, budget
        self.pos = self.transferred = 0
        self.cache = collections.OrderedDict()
    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos+offset if whence == 1 else self.size+offset
        if self.pos < 0: raise ValueError('Negative offset')
        return self.pos
    def read(self, n=-1):
        if n < 0: n = self.size-self.pos
        if n > 4_000_000: raise ValueError('Range audit request too large')
        end, out = min(self.pos+n, self.size), []
        while self.pos < end:
            key = self.pos//524288
            a, b = key*524288, min((key+1)*524288, self.size)-1
            if key not in self.cache:
                if self.transferred+b-a+1 > self.budget: raise ValueError('Audit byte budget exhausted')
                with requests.get(self.url, headers={'Range':f'bytes={a}-{b}', 'Accept-Encoding':'identity'}, stream=True, timeout=45) as r:
                    if r.status_code != 206: raise ValueError(f'Range unsupported: {r.status_code}')
                    if r.headers.get('Content-Range') != f'bytes {a}-{b}/{self.size}':
                        raise ValueError('Unexpected Content-Range: '+r.headers.get('Content-Range',''))
                    data=r.content
                    if len(data)!=b-a+1: raise ValueError('Unexpected range length')
                self.cache[key]=data
                self.transferred+=len(data)
                if len(self.cache)>16: self.cache.popitem(last=False)
            take=min(end,b+1)-self.pos
            out.append(self.cache[key][self.pos-a:self.pos-a+take]); self.pos+=take
        return b''.join(out)

def audit_erk():
    metadata=json.loads((ROOT/'zenodo7808385.json').read_text())
    item=metadata['files'][0]
    stream=RangeFile(item['links']['self'],item['size'])
    result={'record':7808385,'archive_bytes':item['size'],'publisher_checksum':item['checksum'],
            'whole_archive_checksum_verified':False,'license_metadata':metadata['metadata'].get('license'),
            'full_member_audits':[], 'header_previews':[]}
    with zipfile.ZipFile(stream) as z:
        names=z.namelist()
        descr=next(n for n in names if n.endswith('column_descriptions.md'))
        (ROOT/'ERK_COLUMN_DESCRIPTIONS.md').write_bytes(z.read(descr))
        for suffix in ['binary_rep1_pos01_period5.csv','binary_rep1_pos02_period5.csv']:
            name=next(n for n in names if n.endswith(suffix))
            # A complete small member verifies ZIP CRC and produces an independent SHA-256.
            data=z.read(name)
            rows=csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
            fields=rows.fieldnames
            counts=collections.Counter(); flags=collections.defaultdict(set); timeline=collections.defaultdict(set)
            for row in rows:
                tid=row.get('track_id',row.get('track', 'UNAVAILABLE'))
                counts[tid]+=1
                flags[tid].add(row.get('is_preselected','UNAVAILABLE'))
                t=row.get('time_in_minutes',row.get('time','UNAVAILABLE'))
                timeline[t].add(row.get('is_light_pulse','UNAVAILABLE'))
            times=sorted(timeline,key=float)
            entry={'member':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                   'zip_crc_verified':True,'columns':fields,'rows':sum(counts.values()),'tracks':len(counts),
                   'rows_per_track':dict(collections.Counter(counts.values())),
                   'selection_flag_per_track':dict(collections.Counter('|'.join(sorted(v)) for v in flags.values())),
                   'times_minutes':[float(t) for t in times],
                   'stimulus_values_by_time':{t:sorted(timeline[t]) for t in times},
                   'response_values_analyzed':False}
            result['full_member_audits'].append(entry)
            print(suffix, 'rows',entry['rows'],'tracks',entry['tracks'],'flags',entry['selection_flag_per_track'], 'columns',fields,flush=True)
        for folder in ['interval_encoding/','interval_encoding_with_minimal_gap/']:
            name=next(n for n in names if folder in n and n.endswith('.csv'))
            with z.open(name) as member:
                header=member.readline().decode('utf-8-sig').strip()
            result['header_previews'].append({'member':name,'header':header,'full_member_crc_verified':False})
        result['network_bytes']=stream.transferred
    (ROOT/'ERK_ACCESS_AUDIT.json').write_text(json.dumps(result,indent=2))
    print('ERK network bytes',stream.transferred,flush=True)

if __name__=='__main__':audit_erk()
