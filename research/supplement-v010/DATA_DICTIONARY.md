# Supplementary data for v0.10

Data S1–S9 are byte-preserved in `../supplement-v08/data/`; all files are included in the complete package. Data S10 is in `../supplement-v09/data/`; Data S11 is in `data/` alongside this dictionary. The retained directory names identify immutable data, not missing earlier editions.

# Supplementary data dictionary

All CSV fractions use exact numerator/denominator strings. Integer counts are design or enumeration counts. No file contains biological measurements.

| File | Rows / representation | Meaning |
|---|---|---|
| Data_S1_polynomial_coefficients.csv | 332 nonzero terms | Current and source symbols; exponents of b0 and b1; coefficients computed separately for schedules A and B. Omitted terms are zero. Coefficient sums are 288 for each current symbol. |
| Data_S2_structure.json | Exact structural certificate | Two strings, symbol-labelled cyclic runs, autocorrelations and symmetry exclusion. Autocorrelation arrays are integer numerators with denominator 24. |
| Data_S2_cyclic_word_counts.csv | Observed cyclic words through order eight | Count under each schedule, including zero for a word observed only in the other schedule. A word absent from both has zero counts. Leading zeros in the word column must be preserved as text. |
| Data_S3_instrument_phase_initial.csv | 96 rows | Four joint initial states and 24 phases; exact instrument fractions and deviations computed within each run before pooling. Joint state is 2c+d. |
| Data_S4_deterministic_enumeration.csv | Four rows | All labelled tables by state count. Phase-mean and law columns count table–initial pairs; the common-phase column additionally counts phase-specific comparisons. |
| Data_S4_markov_occupations.csv | Six rows | State–symbol fractions for the three-state witness, ordered state first and symbol second. Each complete profile sums to one. |
| Data_S5_supplement_checks.json | Verification record | Explicit stationary/phase-mean normalization checks and exact finite-promoter transient coefficient checks. Mathematical test parameters are not fitted biological parameters. |

The phase certificate stores integer profiles scaled by 12. A single scaled profile is divided by 288; a sum over 24 such profiles is divided by 6912. The supplementary checker reconstructs the latter independently and rejects use of 288 for that sum. Source hashes identify the producer and checker versions. `SHA256SUMS` covers all other data files.


## Data S6: finite reporter acquisition

`Data_S6_finite_reporter.json` records the full mathematical parameter domain, verifier source hashes, exact-check totals and the window CSV hash. `Data_S6_finite_reporter_windows.csv` records every declared test case; no row is an empirical observation.

- `case`: zero-based parameter-case identifier in the product order specified in `finite_reporter/verify.py`.
- `model`: single-stage or maturation chain; `schedule`: 0 for A, 1 for B; `phase`: cyclic input rotation.
- `initial_promoter`: active probability; `initial_reporter_each_stage`: common initial value assigned to every reporter state in this mathematical case.
- `discarded_periods`, `measured_periods`: integer acquisition lengths.
- `raw_bias_integral`: exact integral of output error relative to the periodic solution over the measured window.
- `corrected_bias_integral`: the raw integral minus the boundary functional; `predicted_corrected_integral`: the independent closed promoter expression. They must be equal.
- `bound_constant`, `bound_log2_coefficient`: the bound on the absolute raw bias integral is their affine combination with log(2). Inequalities are certified with rational logarithm bounds.

To obtain window means, divide each integral or bound by `24 * measured_periods * log(2)`. Exact fractions are stored as text; do not round before checking identities.

## Data S7: delivered-input and timing robustness

`Data_S7_input_robustness.json` gives the full parameter domain, construction dependencies, source hashes and exact counts. `Data_S7_input_robustness_windows.csv` contains 1,728 mathematical windows, not empirical observations.

`case` indexes the product of rate family, synthesis family and reporter architecture described in S11.6; `maturation` is 0 for scalar and 1 for two-stage. `schedule` is 0 for FD7 A and 1 for B; `phase` is the cyclic rotation. `scenario` names ideal, amplitude, delay, alternating_jitter, mixed or history_only. `initial` gives periodic, zero or one initial states; the affine coordinate remains one. Discarded and measured periods use the nominal period 96 log(2).

Every suffix pair `_a`, `_b` represents an integrated quantity `a + b log(2)` as exact rational text. `raw` and `corrected` are signed errors relative to the ideal periodic mean integrated over the window. `coefficient_corrected_bound` and `coefficient_raw_bound` use actual coefficient-error envelopes. `amplitude_corrected_bound` and `amplitude_raw_bound` use the stated global calibration gains times per-arm amplitude error. Divide all these integrals by `96 * measured_periods * log(2)` for the corresponding means. The hypotheses, contraction rates and gains are in the source and certificate; no floating-point rounding is used to decide these inequalities.

The initial standalone execution is retained separately in the internal research report. Current Data S7 is produced by the complete article workflow. A positive timing-kernel weight before acquisition means that discarded observations can still affect the measured state. The common-mode counterexample has unchanged differential exposure and a synthesis-mean contrast of exactly 1/4.

## Data S8: statistical interface

`Data_S8_statistical_inference.json` records the complete finite-law domain, exact audit counts, adverse controls and source hashes. `Data_S8_statistical_cases.csv` contains one row for each law/alpha case: horizon, leaves, nodes, conditional-component and independent count-product checks, exact first-crossing probability and terminal expected e-value. `Data_S8_statistical_crossings.csv` records every horizon 1–64, exact first-crossing probabilities for the valid e-process and repeatedly inspected exact binomial tests, and the nominal alpha. Probabilities are rational strings. These are enumerated mathematical probability laws, not biological observations or Monte Carlo estimates.

## Data S9: count tails and saturation

`Data_S9_count_tails.json` records the declared law domain, exact/certified audit counts, source hashes and adverse controls. `Data_S9_count_tail_cases.csv` contains 360 rows: initial cap, integrated candidate-arrival intensity, positive-geometric batch parameter, saturation threshold, independently enclosed stop-loss expectation, certified upper bound and dominating first/second moments. `Data_S9_count_tail_curves.csv` gives the same comparison for caps 1–40, zero initial count and arrival intensity one, with the second-moment-only bound. `Data_S9_saturation_crossings.csv` gives exact first-crossing probabilities for horizons 1–24 in the equal-mean saturation counterexample, with and without its bias allowance. Fractions are exact text; exponential functions are represented by rigorous outward-rounded intervals. These are mathematical audit inputs and probabilities, not biological measurements.

## Data S10: explicit translation

`Data_S10_translation_moments.json` records all checks, source and CSV hashes and adverse controls. `Data_S10_translation_cases.csv` defines 432 initial-condition/rate cases; `Data_S10_translation_windows.csv` gives 3,888 observation windows with outward-rounded rational enclosures and certified upper budgets. `Data_S10_translation_stationary.csv` contains 81 exact stationary moment/Fano rows. `Data_S10_translation_curves.csv` supplies the 64 Figure 8 time points. Times are multiples of log(2); all rates, initial counts and caps are declared mathematical inputs, not fitted or observed biology. The suffix `lower`/`upper` denotes a rigorous enclosure; `_loss_upper` denotes a one-sided conditional distortion allowance. The radius is for a two-arm corrected contrast. The zero-immigration normalization is explicitly not applicable; finite-time propagation remains valid. See SI S14 for the general conditional theorem and the fixed-rate scope of the independent cluster oracle.


## Data S11: continuous-time occupation discrimination

The files in `data/` contain the kinetic witness. `Data_S11_kinetic_audit.json` records the verifier, full audit counts, source hashes, independent interval certificates and a rate-perturbation bound. `Data_S11_kinetic_certificate.json` gives the two generators, pulse transitions, constant/logarithmic integral matrices, period products, invariant rows and occupation coefficients. Each rational quantity is stored as an exact fraction string.

`Data_S11_kinetic_occupations.csv` has 48 rows: eight durations, two symbols and three states. `Data_S11_kinetic_curves.csv` has 24 rows after summing over symbols. `duration_log2` specifies a pulse duration n log(2); the full period is 24 n log(2). `integral_constant` and `integral_log2` give the a-minus-b integral as A + B log(2). `mean_lower` and `mean_upper` are outward-rounded decimal enclosures after division by the full period, not estimates or standard errors.

`Data_S11_kinetic_perturbations.csv` contains four prescribed rate perturbations. `generator_norm_radius` uses the maximum absolute row-sum norm of the generator difference. The mean interval is independently computed by uniformization; `uniform_lower_bound` is the analytical guarantee covering every qualified generator pair in that norm ball. The certificate records both the rational minorization coefficients and the conservative Lipschitz constant. These inputs are specified model rates, not biological measurements or fitted parameters.
