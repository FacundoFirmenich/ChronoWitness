# Local calibration, new cellular acquisitions and the FD8 design frontier

This campaign couples an exact input-design extension to a provenance-preserving audit of cellular observation. Local jurisdictions retain acquisition, time segment, input transition and fluorescence band; larger sets are reconstructed from their original residuals.

| Study | Evidence | Main finding |
|---|---|---|
| E6 | Retrospective early-selection revision on existing acquisitions | Tail losses above 1% decrease from 20 to 3 on 232 common leaves, with fewer MAE improvements. |
| E8 | Ten additional acquisition dates from the published Lugagne–Blassick–Dunlop dataset | Tail losses decrease from 102 to 62 on 552 common leaves; local adverse transfer remains, including antibiotic acquisitions. |
| FD8 | Finite word search, exhaustive state enumeration and rational kinetic intervals | A 32-pulse pair preserves the three-state deterministic profile-law null and increases one kinetic witness contrast by 60.33% at fixed total period. |

Counts are descriptive over overlapping jurisdictions, not independent experimental replicates. The 32-pulse design matches cyclic words through order nine despite the campaign name FD8. Its fixed-period comparison requires 25% shorter pulses. E8 controls were not FD7 interventions: a complete input audit, independently cross-checked, found no supported FD7 period under the examined widths.

## Verify the distributed numerical evidence

Download `ChronoWitness_E6_E8_FD8_SOURCES.zip`, `E6_RESULTS.zip`, `E8_RESULTS.zip` and `FD8_FINAL_RESULTS.zip` from the same v0.14.0 release. Extract the source archive, place the three result archives in its `campaign/` directory, and run:

```sh
python -m pip install numpy==2.2.6 scipy==1.15.3 matplotlib==3.10.7
cd campaign
python verify_e6.py
python verify_e8.py
python verify_design_profiles.py
python figures.py
```

The independent verifiers reconstruct parent metrics directly from residuals and check early-selection decisions. The Python orbit checker uses a separate state/input-position traversal to check the distinction between phase means and profile laws. The source archive includes the E4 reference needed by the regression verifier.

## Reproduce from the published acquisitions

Source: [Zenodo record 8114649](https://zenodo.org/records/8114649), accompanying [Lugagne, Blassick and Dunlop, Nature Communications 15, 2148 (2024)](https://doi.org/10.1038/s41467-024-46361-1). Preserve upstream attribution and terms; the repository's MIT license covers its code, not a relicensing of third-party data.

Obtain `datasets.zip` and `experiments.zip` from that record. Expected SHA-256:

```text
datasets.zip    03a788ddeaa08d3b9ef1511208c8c37263cc5bd55af7e9b41f4f3068ab5ab529
experiments.zip bf4bbb441327c786604e5b78b1def1c67f282ea471a6cb65ba1cdf9814f12d67
```

Use a separate directory for the roughly 1.77 GB of upstream archives and reconstructed numeric arrays. From `campaign/`:

```sh
python e6.py /path/to/datasets.zip /path/to/new-e6-results
python prepare_e8.py /path/to/archive-directory
python e8_evaluate.py /path/to/archive-directory/experiments.zip /path/to/new-e8-results
```

`prepare_e8.py` creates `E8_PREPARED` and refuses to reuse that destination. It retains series/position/trajectory identifiers, structural validity and original binary inputs. It does not use published error rankings. Fluorescence reconstruction reverses the normalization scale but retains upstream clipping. Frozen protocol and source hashes are included.

## Reproduce the design calculation

`search_fd8.py` uses the included forward and backward occupation-polynomial builders. The source archive also contains the complete exact certificate inputs and evaluators in `design/`:

```sh
python search_fd8.py
cd ../design
g++ -O3 -std=c++17 enumerate_general.cpp -o enumerate
./enumerate 10111111111000101110001000010000 10111000101111111110001000010000 4 > reproduced-states.json
python compare_kinetics.py
```

The first 24-pulse candidate's loss of the three-state null is preserved. The subsequent state-preserving search is explicitly recorded as an addendum. Neither global minimum length nor global optimality is claimed.

## Reading the evidence

`LOCAL_JURISDICTION_CONTRACT.md` specifies inclusions, overlapping support, non-estimable strata and exact pooling. `CIERRE_CIENTIFICO_E6_E8_FD8_ES.md` provides the substantive scientific closure in Spanish. Protocols, full adverse outcomes, source provenance and verification receipts accompany the release. Manuscripts and the confidential commercial annex are not part of the public release.
