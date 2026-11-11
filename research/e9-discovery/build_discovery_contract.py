"""Freeze source selection and acquisition splits before response scoring."""
from pathlib import Path
import collections, datetime, hashlib, json, re

R=Path(__file__).resolve().parent
def write(name, value):
    (R/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

inv=json.loads((R/'ERK_ZIP_INVENTORY.json').read_text())
dated={1:'2021-04-27',2:'2021-04-28',3:'2021-04-29',4:'2021-05-01',5:'2021-05-02'}
cohort=[]
for x in inv:
    m=re.search(r'binary_rep(\d+)_pos(\d+)_period(\d+)\.csv$',x['name'])
    if not m:continue
    rep,pos,period=map(int,m.groups())
    date=dated[rep] if period in (3,10,15) else '2021-04-07' if period in (5,7) else '2019-09-03'
    role=('TRAIN' if rep<=2 else 'CALIBRATION' if rep==3 else 'TEST') if period in (3,10,15) else 'ANCILLARY_DISTINCT_PROTOCOL'
    cohort.append({**x,'date_from_upstream_configuration':date,'export_rep_label':rep,'export_position_label':pos,
                   'clock_minutes':period,'role':role,'independence_cluster':date})
write('E9_COHORT_MANIFEST.json',cohort)
primary=[x for x in cohort if x['role']!='ANCILLARY_DISTINCT_PROTOCOL']
assert len(primary)==30
assert collections.Counter(x['role'] for x in primary)=={'TRAIN':12,'CALIBRATION':6,'TEST':12}
groups={role:{x['independence_cluster'] for x in primary if x['role']==role} for role in ('TRAIN','CALIBRATION','TEST')}
assert not groups['TRAIN']&groups['CALIBRATION'] and not groups['TRAIN']&groups['TEST'] and not groups['TEST']&groups['CALIBRATION']

input_audit=json.loads((R/'INTERVAL_INPUT_PREFIX_AUDIT.json').read_text())
assert len(input_audit['files'])==15
# Independently rescan the actually inspected input minutes with string matching.
words={'FD7a':'101111110010110010001000','FD7b':'100010110010111111001000',
       'FD8a':'10111111111000101110001000010000','FD8b':'10111000101111111110001000010000'}
input_summary=[]
for x in input_audit['files']:
    times=x['observed_minutes']; events=set(x['pulse_minutes']);support=set(times)
    observed=''.join('1' if t in events else '0' if t in support else '?' for t in range(times[0],times[-1]+1))
    hits=set()
    for label,word in words.items():
        for width in range(1,31):
            for phase in range(len(word)):
                rotation=word[phase:]+word[:phase]
                target=''.join(c+'0'*(width-1) for c in rotation)
                at=observed.find(target)
                while at>=0:
                    hits.add((label,times[0]+at,width));at=observed.find(target,at+1)
    old={(m['word'],m['start_min'],m['slot_min']) for m in x['matches']}
    assert hits==old,(x['member'],hits,old)
    input_summary.append({'member':x['member'],'track_id':x['track_id'],'first_minute':times[0],'last_minute':times[-1],
                          'observed_minutes_count':len(times),'continuous_support':len(times)==times[-1]-times[0]+1,
                          'pulse_minutes':sorted(events),'matches':x['matches'],'full_csv_crc_verified':False})
write('INPUT_COMPATIBILITY_RECEIPT.json',{'scope':input_audit['scope'],'widths_minutes':list(range(1,31)),
      'cyclic_rotations':True,'independent_implementations_agree':True,'network_bytes':input_audit['network_bytes'],
      'files':input_summary,'sustained_waveform_equivalence_proved':False,
      'conclusion':'No FD7/FD8 full-cycle pulse-event match within inspected trajectories and widths; no claim outside those jurisdictions.'})

access=json.loads((R/'ERK_ACCESS_AUDIT.json').read_text())
compact=[]
for x in access['full_member_audits']:
    compact.append({k:v for k,v in x.items() if k not in ('times_minutes','stimulus_values_by_time')})
write('ERK_VERIFIED_SCHEMA.json',{'record':7808385,'archive_bytes':access['archive_bytes'],
      'publisher_checksum':access['publisher_checksum'],'whole_archive_checksum_verified':False,
      'full_member_audits':compact,'header_previews':access['header_previews'],'license':'CC-BY-4.0',
      'network_bytes':access['network_bytes']})

protocol={
 'version':'E9-source-and-cohort-1', 'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'SOURCE_AND_COHORT_FROZEN_BEFORE_PREDICTION; E9_OUTCOME_EVALUATION_NOT_RUN',
 'objective':'Evaluate temporal reconstruction and local calibration across independent acquisition days in human MCF-10A optoFGFR/ERK; separately audit compatibility of recorded stimulus protocols with FD designs.',
 'source':{'doi':'10.5281/zenodo.7808385','version':'1.1','license':'CC-BY-4.0','bytes':723609060,'publisher_md5':'4aef737b263424dbdb06e15f827ccad2','whole_archive_hash_verification_required_before_scoring':True},
 'code_provenance':{'repository':'https://github.com/pawelnalecz/pulsatile-information','commit':'03f9a059d91caa2b72873e2317134ea7f7500203',
                    'mapping':'code/core/experiment_manager.py: repeated_pseudorandom_date, experiments and map_to_official_naming'},
 'primary_split':{k:sorted(v) for k,v in groups.items()},
 'primary_counts':{'train_files':12,'calibration_files':6,'test_files':12,'test_days':2,'clocks_minutes':[3,10,15],
                   'compressed_member_bytes':sum(x['compressed'] for x in primary),'uncompressed_member_bytes':sum(x['bytes'] for x in primary)},
 'grouping':'All positions, cells, pulse schedules, overlapping windows and clock periods from one day stay in the same split. File count and cell count are not independent replicate counts.',
 'secondary_domains':{'binary_5_7_min':'16 CSV files from 2021-04-07, one day; retain as ancillary protocol transfer, never split rep labels into independent days.',
                      'binary_20_30_min':'20 CSV files from 2019-09-03, one day; multiple periods can be segments of one acquisition.',
                      'interval':'15 CSV files; input prefixes audited. Freeze acquisition mapping and any predictive roles before response scoring.'},
 'data_contract':{
   'identity':['source_record','member','acquisition_date','clock','field','track_id','time_in_minutes'],
   'input':'is_light_pulse marks a 100 ms flash within the current minute, not sustained illumination during that minute; confirm within-frame alignment from acquisition files before transition scoring.',
   'output':'Use original nuclear ERK-KTR and contemporaneous image intensity, with structural validity flags and no response-amplitude exclusion. A future prediction cannot use future image intensity as a predictor.',
   'causality':'Q3 centered and Q4 whole-track normalization are disallowed in prospective prediction. The CSV export uses Q3backw, which is backward-looking; do not mislabel that exported column as future-leaking. Recompute causal variants from source fields and verify correspondence.',
   'selection':'Retain every structurally usable exported track, including is_preselected=False. Report the 400-track published subset as a sensitivity only. The exported 500 were already selected by duration/nuclear-area stability, so full-population representativeness remains unestablished.',
   'missingness':'No interpolation, no zero-filling, no response clipping. Report unsupported windows, missing timestamps and conflicting input labels.',
   'statistical_unit':'Day/acquisition for transport evidence; cells and overlapping windows retain dependence. Two held-out days do not support broad population or clinical claims.'},
 'local_jurisdictions':{
   'nesting':'domain > acquisition day > clock protocol > field > cell > temporal segment; cross these with horizon, time since pulse, preceding input history and calibration support.',
   'predefinition':'Define partitions with input/timing/structural metadata or training-only cutpoints. Do not select test jurisdictions by observed benefit.',
   'edges':'Matched cell/time/support comparisons of baseline, unguarded calibration and guarded local policy; spatial geometric proximity is distinct from a measured biological connection.',
   'aggregation':'Retain atomic residual identities; reconstruct parent sums and distributions without duplicate membership. Local harms, tails and coverage are primary; global RMSE/MAE are complementary.',
   'unresolvable':'Keep NOT_ESTIMABLE and OUT_OF_SUPPORT with their support and reason; no zero-effect substitution.'},
 'next_execution_gates':[
   'Verify complete archive checksum remotely, canonical headers and full input consensus across tracks for each used CSV.',
   'Reconcile timestamp trimming, experiment onset and pulse-to-image order; freeze alignment/sensitivity without inspecting prediction scores.',
   'Fit domain-specific reference models on TRAIN only; E. coli coefficients and cuts are not biologically transferable by fiat.',
   'Freeze horizons, history lengths, local cutpoints, early-fit/validation/late windows, purge intervals, support thresholds and policy choices in a numerical E9 evaluation protocol before evaluating TEST.',
   'Run paired local comparisons on identical support, retaining adverse and unresolved jurisdictions; record all candidate choices.',
   'Treat a pulse-block alphabet extension of FD identities as a separate mathematical obligation. Require both delivered arms and acquisition assumptions before calling any dataset direct FD validation.'
 ],
 'compute':'CPU-only sequential CSV/chunk processing; no full image segmentation for E9. A 4 GB peak-memory claim and runtime estimate require a pilot measurement; neither is asserted here.',
 'not_changed':['E6/E8 results','FD7/FD8 mathematical certificates','existing manuscript results','historical adverse findings'],
}
write('E9_SOURCE_PROTOCOL.json',protocol)

registry=[
 {'id':'ERK_HUMAN_2023','priority':1,'decision':'PRIMARY_EXECUTABLE_DOMAIN','paper':'https://doi.org/10.1371/journal.pcbi.1011155','data':'https://doi.org/10.5281/zenodo.7808385','archive_bytes':723609060,'csv_files':81,'verified_full_csvs':2,'verified_full_csv_rows':199701,'unique_track_ids_are_local_to_file':True,'intervention':'100 ms light pulses; 1 min sampling','new_authority':'Independent-laboratory cellular signaling domain; temporal/local transport evaluation','direct_fd_validation':'NOT_ESTABLISHED'},
 {'id':'SPATIAL_CAMP_ERK_2022','priority':2,'decision':'SPATIAL_EXTENSION_PENDING_DATA_ACCESS_AND_REPROCESSING','paper':'https://doi.org/10.1371/journal.pcbi.1009873','data':'https://doi.org/10.7272/Q6QC01RN','code':'https://github.com/mikechevy/emitter-receiver-paper','archive_bytes':9242972535,'data_download_api_http':401,'public_download_http':403,'small_archives_verified':['image_load_files.zip','process_imaging_data_MATLAB_Paper.zip'],'schema_finding':'Two MATLAB examples contain nuclear coordinates, bPAC labels and nuclear masks; they do not contain a complete matched ERK trajectory/stimulus table. Whole-cell membrane contacts cannot be inferred from nuclear masks.','license_caution':'No repository code license detected; do not relicense or redistribute as MIT.'},
 {'id':'OPTOCLOCK_2024','priority':3,'decision':'SMALL_LOCAL_VS_AGGREGATE_SECONDARY_BENCHMARK','paper':'https://doi.org/10.7554/eLife.97754','data':'https://cdn.elifesciences.org/articles/97754/elife-97754-data3-v1.xlsx','bytes':125909,'schema_verified':True,'series':'6 synchronization channels, 10 entrainment channels; one sheet per condition','time_step_min':9,'stimulus':'Green intervals annotated in hours; background red light, not binary dark/blue assay','limitations':'The workbook covers figures 4b and 5e. Do not claim that figure 6c half-frequency single-cell traces are present. Small number of experiments; no population-wide inference.'},
 {'id':'YEAST_TRANSFER_2021','priority':4,'decision':'RESERVE_FOR_ENDPOINT_DISTRIBUTION_AND_INPUT_FAMILY_DOMAIN','paper':'https://doi.org/10.1016/j.cels.2021.08.003','data':'https://doi.org/10.5281/zenodo.5116822','archive_bytes':4943265429,'metadata_verified':True,'full_data_inspected':False,'design':'119 optogenetic input conditions; single-cell flow cytometry endpoints','limitation':'Independent cells at snapshots are not longitudinal trajectories; cannot reuse temporal early/late calibration unchanged.'},
 {'id':'MAMMALIAN_PROMOTERS_2023','priority':5,'decision':'MECHANISTIC_REFERENCE_NOT_READY_PUBLIC_TRAJECTORY_BENCHMARK','paper':'https://doi.org/10.1093/nar/gkad273','evidence':'Article explicitly states no data deposited in external repositories; supplemental material may support narrower analyses. No author contact performed.'},
 {'id':'YEAST_PP7_2018','priority':6,'decision':'RESERVE_RAW_MATCHED_RECORDS_NOT_LOCATED','paper':'https://doi.org/10.1016/j.molcel.2018.04.012','evidence':'Nascent transcription and light control are relevant; a public machine-readable matched input/trajectory repository was not located in this search. This is not a proof of nonexistence.'},
]
write('CANDIDATE_REGISTRY.json',registry)
write('DISCOVERY_VALIDATION.json',{'primary_manifest_files':30,'split_roles':dict(collections.Counter(x['role'] for x in primary)),
 'date_overlap_between_primary_splits':False,'interval_input_files':15,'independent_input_scans_agree':True,
 'exact_full_cycle_matches_in_inspected_support':sum(len(x['matches']) for x in input_summary),
 'physical_fd_intervention_validation':False,'e9_predictive_results_computed':False})
print(json.dumps({'manifest_files':len(cohort),'primary_files':len(primary),'input_scan_files':15,'status':'VERIFIED_SOURCE_SELECTION'},ensure_ascii=False))
