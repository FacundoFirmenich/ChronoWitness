"""E2-A retrospective temporal calibration on the actual E1 biological arrays."""
from pathlib import Path
import csv
import hashlib
import json
import sys
import time
import numpy as np
import benchmark as e1

HERE = Path(__file__).resolve().parent
P = json.loads((HERE/'E2_PROTOCOL.json').read_text())
OUT = HERE/'e2_results'

def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')

def corrections(pred, target):
    pm, ym = float(pred.mean()), float(target.mean())
    pc, yc = pred-pm, target-ym
    variance = float(pc@pc)
    degenerate = variance == 0
    slope = 1.0 if degenerate else max(0.0, float(pc@yc)/variance)
    intercept = ym-slope*pm
    assert np.isfinite([slope, intercept, ym-pm]).all()
    # These identities check the actual fitted calibration samples, not synthetic data.
    assert abs(float((pred+(ym-pm)-target).mean())) < 1e-8
    residual = slope*pred+intercept-target
    assert abs(float(residual.mean())) < 1e-8
    if slope > 0 and not degenerate:
        assert abs(float(pc@residual))/max(variance, 1.0) < 1e-8
    return {'raw': (1.0, 0.0), 'offset': (1.0, ym-pm),
            'nonnegative_affine': (slope, intercept)}, degenerate

def main():
    start = time.monotonic(); OUT.mkdir(exist_ok=True)
    path = Path(sys.argv[1])
    digest = hashlib.sha256()
    with path.open('rb') as f:
        while block := f.read(1024*1024): digest.update(block)
    assert digest.hexdigest() == P['archive_sha256']
    # Frozen base models were just refitted on the four original training experiments.
    records = json.loads((e1.OUT/'FITTED_MODELS.json').read_text())
    fitted = {(r['offset'], r.get('horizon'), r['model']): r for r in records}
    data = e1.load(path)
    metrics, calibrations, windows = [], [], []
    for offset in P['offsets']:
        for h in P['horizons_frames']:
            for date in e1.P['test_dates']:
                d = data[date]
                cells, origins, availability = e1.samples(d, h, offset)
                target = d['fluo1'][cells, origins+h]
                current = d['fluo1'][cells, origins]
                evaluation = origins >= P['evaluation_first_origin']
                assert evaluation.any()
                assert np.min(origins[evaluation]-11) > max(P['calibration_last_target_frames'])
                predictions = {
                    'persistence': current,
                    'common_relaxation': e1.relax_predict(d,cells,origins,h,offset,
                        fitted[(offset,None,'common_relaxation')]['coefficients'])
                }
                for model in e1.MODELS:
                    r = fitted[(offset,h,model)]
                    predictions[model] = current + e1.features(d,cells,origins,h,offset,model)@np.array(r['coef'])+r['intercept']
                for cutoff in P['calibration_last_target_frames']:
                    calibration = origins+h <= cutoff
                    assert calibration.any() and not (calibration & evaluation).any()
                    assert np.max(origins[calibration]+h) < np.min(origins[evaluation]-11)
                    windows.append(dict(date=date,offset=offset,horizon=h,cutoff=cutoff,
                        n_calibration=int(calibration.sum()), n_evaluation=int(evaluation.sum()),
                        latest_calibration_target=int(np.max(origins[calibration]+h)),
                        earliest_evaluation_feature=int(np.min(origins[evaluation]-11)),
                        evaluation_zero_targets=int((target[evaluation]==0).sum()), **availability))
                    for model, prediction in predictions.items():
                        params, degenerate = corrections(prediction[calibration],target[calibration])
                        calibrations.append(dict(date=date,offset=offset,horizon=h,cutoff=cutoff,
                            model=model,constant_prediction_fallback=degenerate,parameters=params))
                        for method, (slope, intercept) in params.items():
                            corrected = slope*prediction[evaluation]+intercept
                            metrics.append(dict(date=date,offset=offset,horizon=h,cutoff=cutoff,
                                model=model,method=method,n=int(evaluation.sum()),
                                **e1.metrics(corrected,target[evaluation])))
                print(json.dumps(dict(stage='E2',date=date,offset=offset,horizon=h)),flush=True)
    assert len(metrics)==P['expected_metric_rows']
    assert len(calibrations)==P['expected_calibration_records']
    # Raw results must be invariant to cutoff because every cutoff uses the same evaluation set.
    reference = {}
    for row in metrics:
        if row['method'] != 'raw': continue
        key = row['date'], row['offset'], row['horizon'], row['model']
        values = row['n'], row['rmse'], row['mae'], row['bias']
        if key in reference: assert values == reference[key]
        reference[key] = values
    save('METRICS.json',metrics); save('CALIBRATION_FITS.json',calibrations)
    save('WINDOWS.json',windows)
    with (OUT/'METRICS.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(metrics[0]));writer.writeheader();writer.writerows(metrics)
    save('RUN.json',dict(status='COMPLETE_RETROSPECTIVE_E2_A',metric_rows=len(metrics),
        calibration_records=len(calibrations),window_records=len(windows),elapsed_seconds=time.monotonic()-start,
        archive_sha256=digest.hexdigest(),protocol_sha256=hashlib.sha256((HERE/'E2_PROTOCOL.json').read_bytes()).hexdigest(),
        temporal_separation_checks='PASS',same_evaluation_windows_across_cutoffs='PASS',
        actual_sample_calibration_identities='PASS',direct_FD7_validation=False))

if __name__ == '__main__': main()
