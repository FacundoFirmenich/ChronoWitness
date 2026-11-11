# Cellular observations: prediction, transport and local support

The studies complement the exact temporal-input identity by examining the observation layer. Published measurements originate from Lugagne, Blassick and Dunlop, Nature Communications 15:2148 (2024), https://doi.org/10.1038/s41467-024-46361-1; processed data: https://doi.org/10.5281/zenodo.8114649 (CC-BY-4.0).

E1 retains four original training experiments and three original evaluation experiments. Adding input to fluorescence history yields primary 60-minute RMSE reductions of 4.9729%,17.0950%,17.0921%. The first is approximately 5%; its 0.0271 percentage-point shortfall against the original descriptive criterion is retained in the record. E2 transports early offset/affine calibration to later windows and finds mixed outcomes. E3 selects correction from temporally separate early validation, retaining 13 RMSE gains,3 losses and38 unchanged predictions across54 correlated combinations. E4 resolves transport into local context, support and error distributions.

| Local policy on the same270 supported jurisdictions | MAE gains >1% | Losses >1% | Practical ties |
|---|---:|---:|---:|
| Offset |127|80|63|
| Affine |160|75|35|
| Fixed equal-weight mixture |170|41|59|
| Early selection |129|0|141|

Mean improvement does not guarantee tail improvement: selection increases upper-tail mean error in31 supported jurisdictions. The source data, overlapping windows, horizons and alignments do not form independent repetitions of those counts. Program edges are observed input transitions, not inferred regulatory edges. The studies do not infer promoter-state count or validate the FD7 pair in cells.

## Reproduce and inspect

- E1/E2: research/e2-memory-check/, including the frozen base protocol, benchmark, calibration code and measured evidence archive.
- E3: research/e3-calibration-transport/, including nested grouped model selection and all early decisions.
- E4: research/e4-local/, including the complete support ledger, metrics and independent package verification.

The original mathematical and trajectory-Monte-Carlo reproduction remains `python reproduce_release.py`; external-data studies have their own data retrieval and execution instructions. They share pinned NumPy2.2.6 and SciPy1.15.3. No laboratory or commercial document is distributed in this repository.
