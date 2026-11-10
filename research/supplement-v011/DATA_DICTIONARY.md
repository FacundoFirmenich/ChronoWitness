# Data for the v0.11 scientific edition

Data S1–S9 remain in `supplement-v08/data/`, Data S10 in `supplement-v09/data/`, and Data S11 in `supplement-v010/data/`. Their original definitions and normalization are retained in the v0.10 data dictionary. Current Data S12 is in this directory's `data/` subdirectory.

| File | Meaning |
|---|---|
| `Data_S12_design_search.json` | Frozen protocol hash, every numerical seed outcome, rationalized rates, termination status and selected candidate. |
| `Data_S12_design_certificate.json` | Rational generators, integrated-occupation intervals, gain bounds, minorization and half-margin rate radius; independent uniformization controls. |
| `Data_S12_design_power.csv` | Mixture, mean tolerance, positive-score probability, mean, block horizon, exact rational and decimal first-crossing probability, and null/alternative role. |
| `Data_S12_design_power.json` | Scope, row count, independent path-check count and CSV hash. |
| `Data_S12_design_tutorial.json` | Exact promoter integral, reporter null, certified kinetic lower margin and sufficient fixed-horizon block count for the declared ideal observation. |
| `Data_S12_design_controls.json` | The FD7 and matched-run control words, structural counts, polynomial equality and exact promoter integral contrast. |

Rates in the design search are measured in inverse units of the common unit pulse duration. Occupation contrasts are dimensionless fractions. Generator perturbations use maximum absolute row-sum norm. Power probabilities are conditional on the declared iid two-point block law; they are not calibrated biological probabilities. The tutorial uses a distinct paired-state observation model.

The protocol and scripts live in `design_frontier/`. `SHA256SUMS` records the exact distributed data bytes.
