# Scientific results and interpretation

[Castellano](RESULTADOS_CIENTIFICOS.md)

ChronoWitness studies what a temporal input can distinguish when the readout is fixed. Its FD7 pair is designed to match several common summaries while separating particular classes of dynamical readers.

## The central result

Both schedules contain 24 binary symbols, twelve of each kind. They have the same cyclic word counts through order seven, symbol-labelled run multiset and cyclic autocorrelation. Their two-state occupation polynomials coincide exactly. Consequently every strictly positive two-state Markov reader in the declared periodic occupation class shares the same profile under both schedules. The continuous-time promoter identity and a common stable linear reporter cascade transport this equality to period-averaged expression.

The state thresholds combine a lower-class exclusion with an explicit separating reader. Four deterministic states are necessary and sufficient for the phase-balanced profile law. Three positive Markov states, and three positive continuous-time kinetic states, suffice for their respective occupation observables. This is an existence statement at the threshold, not a claim that every larger reader separates the inputs.

## From existence to a larger margin

The first kinetic witness uses integer spectra and rational pulse propagators to make the state-threshold proof transparent. Its state-zero contrast is about 1.03e-6. A separately declared search over positive generator rates produces a rational candidate with integrated contrast between 0.0100794705475041 and 0.0100794705475042 for a state indicator normalized to [0,1].

The candidate is verified by outward-rounded uniformization and a Markov-tree invariant-distribution calculation. A quantified perturbation neighborhood retains half its margin. All three search runs reached their fixed generation budget; the result establishes a certified improvement, not global optimality.

## The observation pathway

Finite acquisition can retain promoter and reporter transients. Endpoint correction eliminates the reporter initial-state contribution when its required endpoint functional is observable. Otherwise, raw-window contraction bounds provide a different route. Delivered amplitude and timing errors require per-arm information; detector saturation requires a bound on the change of conditional mean. The explicit translation envelope retains mRNA–protein correlations and degradation.

## Statistical inference

The test operates on experimental blocks with justified conditional mean tolerance and bounded support. Predictable stakes and the supplied fixed mixtures preserve validity under optional stopping. Exact prefix counting evaluates first-crossing probabilities under declared two-point block laws. These calculations expose the effect of tolerance and stake allocation without assigning an unmeasured noise law to a biological assay.

## Design provenance

The distributed FD7 v0.7.0 certificate fixes the design pair and its structural claims. Independent programs reproduce them. The retained certificate is not a discovery log, and neither minimal length nor a general FD_k construction is inferred from it. The additional matched-run control shows that equal dose, run multiset and switch count alone do not imply the occupation identity.

## Evidence map

| Result | Implementation | Distributed evidence |
|---|---|---|
| Matched design and deterministic threshold | `research/analysis/` | Data S1–S4 |
| Two-state occupation criterion | `research/analysis/verify_markov_boundary.py` | Polynomial certificates and reference outputs |
| Finite reporter and delivery bounds | `research/finite_reporter/`, `research/input_robustness/` | Data S6–S7 |
| Statistical interface and saturation | `research/statistical_inference/`, `research/count_tails/` | Data S8–S9 |
| Explicit catalytic translation | `research/translation_counts/` | Data S10 |
| Spectral kinetic witness | `research/kinetic_reader/` | Data S11 |
| Larger certified witness, power and controls | `research/design_frontier/` | Data S12 |
