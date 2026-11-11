"""Audit recorded pulse events only, preserving the inspected time jurisdiction.

This does not equate 100 ms flashes with sustained light or certify FD nulls.
Only the first exported trajectory per interval file is read. Coverage outside
that trajectory is unobserved here; all such boundaries remain explicit.
"""
import csv, io, json, zipfile
from audit_public_sources import ROOT, RangeFile

WORDS={'FD7a':'101111110010110010001000','FD7b':'100010110010111111001000',
       'FD8a':'10111111111000101110001000010000','FD8b':'10111000101111111110001000010000'}

def scan(times, pulses):
    support=set(times); events=set(pulses); hits=[]
    for label,word in WORDS.items():
        rotations=sorted({word[k:]+word[:k] for k in range(len(word))})
        for width in range(1,31):
            length=len(word)*width
            for start in times:
                stop=start+length
                if stop-1>times[-1] or any(t not in support for t in range(start,stop)):continue
                within={t-start for t in events if start<=t<stop}
                if any(t%width for t in within):continue
                observed=''.join('1' if k*width in within else '0' for k in range(len(word)))
                if observed in rotations:
                    hits.append({'word':label,'start_min':start,'slot_min':width,'cycles':1})
    return hits

def main():
    meta=json.loads((ROOT/'zenodo7808385.json').read_text())['files'][0]
    remote=RangeFile(meta['links']['self'],meta['size'],budget=40_000_000)
    out={'scope':'first exported track per interval file; input values only; minute pulse-event encoding',
         'widths_minutes':list(range(1,31)),'all_cyclic_rotations':True,
         'physical_sustained_light_equivalence_established':False,'files':[]}
    with zipfile.ZipFile(remote) as z:
        names=sorted(n for n in z.namelist() if n.endswith('.csv') and '/interval_encoding' in n)
        for name in names:
            times=[];events=[];first=None
            with z.open(name) as f:
                rows=csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig'))
                for row in rows:
                    tid=row['track_id']
                    if first is None:first=tid
                    if tid!=first:break
                    t=float(row['time_in_minutes']);u=float(row['is_light_pulse'])
                    if not t.is_integer() or u not in (0,1):raise ValueError('Unexpected input format')
                    times.append(int(t))
                    if u:events.append(int(t))
            assert times==sorted(set(times)), 'Track time ordering changed'
            hits=scan(times,events)
            entry={'member':name,'track_id':first,'observed_minutes':times,'pulse_minutes':events,
                   'full_member_crc_verified':False,'matches':hits}
            out['files'].append(entry)
            (ROOT/'INTERVAL_INPUT_PREFIX_AUDIT.json').write_text(json.dumps(out,indent=2))
            print(name.split('/')[-1],len(times), 'minutes',len(events),'pulses','matches',len(hits),flush=True)
    out['network_bytes']=remote.transferred
    (ROOT/'INTERVAL_INPUT_PREFIX_AUDIT.json').write_text(json.dumps(out,indent=2))

if __name__=='__main__':main()
