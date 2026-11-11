# E5 — Nested jurisdictions and aggregation masking

This retrospective audit retains the complete local structure of ChronoWitness E4 while reconstructing its containing sets. It evaluates saved summaries of measured cellular trajectories; it neither simulates new cells nor refits a predictor.

For each fixed experimental date, alignment, and horizon, temporal segment × programmed input edge × fluorescence band define 36 elementary jurisdictions. All unrestricted/restricted coordinate combinations plus an explicit empty intersection form an 81-node, 220-edge inclusion lattice. The 18 cases stay separate: horizons and alignments share observations and are not independent replications. The join is the smallest represented containing set and need not equal the literal union.

On the same 270 jointly supported leaves, local selection retains nonnegative MAE improvement in all 544 nonempty containing sets. This is an additive-loss consequence of the leaf results, not a fresh validation sample. RMSE reveals two local losses above 1% and two favorable containing sets that mask them. Both losses belong to the April 15 experiment, 30-minute horizon, late segment, input 11 and middle fluorescence under the two alignments. Under the primary alignment, local MAE improves 3.24% while RMSE deteriorates 1.06% and the top-5% mean deteriorates 2.59%; the containing input-11 set improves RMSE 1.04%. The 31 E4 local tail deteriorations remain.

## Reproduction

Extract the archive preserving both sibling directories. From `e5-nested-20261111`, run:

```sh
python reproduce.py
python verify.py
```

`reproduce.py` uses the standard library, writes a fresh `reproduced-results` directory and checks every derived scientific output against the saved reference. Discrete fields must match exactly; floating values use relative tolerance 2e-12 and absolute tolerance 1e-8, matching the independent reconstruction check. Every floating difference is counted and sampled in the receipt. Elapsed time and gzip timestamps are excluded. The initial Windows-to-Linux run failed a decompressed-CSV byte-equality check; its failure is preserved in the execution history. For another run choose `--output ANOTHER_NEW_DIRECTORY`. No reference result is overwritten. `verify.py` additionally needs NumPy; local verification used NumPy 2.3.5. It reconstructs values independently through an incidence matrix and checks intersections, joins and cover relations. Optional figure regeneration uses Matplotlib 3.10.7: `python figures.py`.

## Evidence boundaries

- The protocol was fixed before E5 outputs, after E4 had been inspected. This is retrospective development, not independent confirmation.
- MAE, MSE and signed bias aggregate exactly with observation counts; RMSE is the square root of aggregated MSE. Relative improvements are not averaged directly.
- Three support domains are kept separate. Support is inherited at the elementary jurisdiction; unique trajectories in overlapping sets are not added as independent samples.
- Intermediate-node pooled quantiles and tail means are not recoverable exactly from saved E4 summaries. They are explicitly marked rather than replaced by averages of local tails.
- Threshold sensitivity is reported at 0%, 0.1%, 1% and 5%. Labels are descriptive, not significance or biological thresholds.
- The audit does not estimate Fisher information or infer a biological topology, causal effect or direct FD7 cellular response.

Code is released under the parent repository's MIT license. Original measured data remain attributed to Lugagne, Blassick and Dunlop (2024), Zenodo 8114649, under the source license. This reproduction archive contains computational summaries, source and figures; manuscripts and commercial annexes are excluded.
