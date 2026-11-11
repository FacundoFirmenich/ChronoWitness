# E11 · Causal calibration across nested jurisdictions

E11 develops a temporal correction on E9/E10 and reserves 14 interval-stimulation acquisitions to evaluate one selected policy. The input history and base predictor remain frozen; the intervention changes only error calibration.

## Causal update

At prediction time t, admissible errors belong to the same cell and have already observed targets: s+h<t. The policy retains a 180- or 360-minute memory and at most the 12 most recent prediction intervals with non-overlapping interiors. This prevents indefinite reuse of an initial bias; it does not make observations or their histories independent.

The nested variant seeks support in cell × pulse phase × signal band, then cell × pulse phase, then cell. Signal bands come exclusively from E9 TRAIN. The control variant uses the cell level only. At least six mature errors are required, with at least three in each of two chronological blocks.

When the two block means have the same nonzero sign, the proposal is

`c = shrink * sign(mu_recent) * min(abs(mu_older), abs(mu_recent))`,

with shrink 0.25 or 0.5. The proposal is admitted only when the corrected absolute-error 95th percentile in each historical block is at most 1.01 times its original value. Otherwise the base prediction is retained. A supported jurisdiction that fails this criterion cannot fall back to a broader jurisdiction merely to force a correction.

Agreement and tail checks are historical admission rules. They are neither future-mean confidence bounds nor prospective no-harm guarantees. Feedback always uses the base predictor's residuals, not the corrected predictor's residuals.

## Development and reserved evaluation

Eight combinations are compared on four acquisition dates already examined in E9/E10. Candidates are rejected if they act on fewer than 1% of windows on any date or if their mean daily relative RMSE exceeds 1.05. Among admissible candidates, selection first minimizes the worst daily mean fraction of pulse/signal jurisdictions with q95 harm above 1%, then its mean across dates, then the mean daily log RMSE ratio. Identifiers break ties. These are design criteria, not significance tests.

`SELECTED_POLICY.json` is generated before the reserve is scored. If no candidate is admissible, the reserve remains unscored. The selected candidate is compared on identical late windows with the base predictor, signal-history-only predictor, persistence and fixed E9 guard. Previously matured late outcomes may enter later updates: this is sequential evaluation with feedback.

Horizons remain 5, 10 and 20 minutes; both alignments are retained. The predictor is not changed using reserved outcomes. As in E9, the base predictor uses scheduled future inputs: prediction is conditional on a known stimulation program.

The updated policy uses mature late residuals, whereas the fixed guard retains its early bias. Their comparison evaluates the entire update, memory, shrinkage and locality regime; it does not isolate the causal effect of nesting. Cell-only variants and alternative memories are used for development and selection, not scored as additional candidates on the reserve.

Parent views, cells, pulse/signal intersections, temporal segments and their intersections are preserved. Nodes with fewer than 20 windows retain LOW_SUPPORT. Parent MSE is reconstructed from each disjoint partition. Percentiles are calculated from atomic observations, never by averaging child percentiles.

## Provenance and scope

The 14 reserved dates are disjoint from E9/E10 and come from the same study and laboratory. Some precede E9 training: this is retrospective transport between acquisitions. `min15_optmean_rep1.csv` remains quarantined because its source folder indicates 2020-02-08 while its acquisition identifier indicates 2020-02-09. Neither date is invented or silently preferred; predictive outcomes for this record are not calculated.

Files, cells and windows are not independent-replicate counts. The stability resampling uses paired summaries of observed acquisitions. It creates no cellular trajectories and does not treat windows as independent. Its percentile interval describes sensitivity to resampling this observed bank, not population representativeness.

The inputs do not implement paired physical FD7/FD8 arms. These results concern predictive transport and calibration, separately from temporal-identity certificates. The ledger retains 6/756 pulse/signal and 81/2268 fine nodes with q95 harm above 1%; uniform local no-harm is not established.

## Reproduction

Create `E11_INPUTS.zip` containing `e9_core.py`, `MODEL_SELECTION.json`, `E9_NUMERICAL_PROTOCOL.json`, `policy.py`, `COHORTS.json` and `E11_PROTOCOL.json`. Copy it with `preflight.py`, `run_e11.py` and `analyze_reserve.py` to `/content` in a fresh Colab CPU runtime.

1. Run `python /content/preflight.py`. It installs NumPy 2.2.6, pandas 2.2.3 and Numba 0.61.2, downloads and verifies the source archive, and audits the 62 admitted CSV inputs.
2. Run `python /content/run_e11.py development`. It retains all comparisons and freezes one admissible policy, if one exists.
3. Only after `SELECTED_POLICY.json` records `FROZEN_BEFORE_RESERVE`, run `python /content/run_e11.py reserve`.
4. After all 84 reserved contexts finish, run `python /content/analyze_reserve.py`; this also requires matplotlib.

Outputs reside in `/content/chronowitness-e11-20261111`. Separate audits reconstruct metrics, risk identities and maturation. The predictor is checked through two algebraic expressions; the policy is checked against another implementation and future-error masking. These checks do not constitute an independently fitted predictor. Drive is not mounted automatically; historical custody used an authenticated connector and complete-byte readback.

## Licences

Original code: MIT. Data: [Zenodo 7808385 v1.1](https://doi.org/10.5281/zenodo.7808385), CC-BY-4.0; [primary article](https://doi.org/10.1371/journal.pcbi.1011155). Date attribution retains upstream commit `03f9a059d91caa2b72873e2317134ea7f7500203`. Source licences remain applicable. Private manuscripts and the commercial annex are excluded. Historical receipts remain preserved in their original language.
