# Data S13: trajectory observation and calibration

Data S1–S12 retain their versioned directories and meanings. Data S13 adds:

| File | Contents |
|---|---|
| `Data_S13_assay_audit.json` | Frozen-protocol hash, 96 moment checks, four exact-power benchmarks, 72 power settings with seed counts and pointwise/simultaneous intervals, source and output hashes |
| `Data_S13_assay_moments.json` | Independently cross-checked state-occupation moments and reporter means |
| `Data_S13_assay_validation_raw.csv` | Path-simulation moments by model, arm, window and seed |
| `Data_S13_assay_power_raw.csv` | Crossing counts by model, window, mixture, tolerance, horizon and seed |
| `Data_S13_assay_benchmark_raw.csv` | Monte Carlo crossings for the four exact-reference laws |
| `Data_S13_assay_calibration.csv` | All 48 rational calibration configurations, bias, range, guaranteed gap and sufficient-block bound when positive |
| `Data_S13_assay_calibration.json` | Exact calibration and box-extreme checks |
| `Data_S13_assay_models.txt` | Explicit generator and periodic-initialization inputs to the trajectory engine |
| `Data_S13_application.json` | Schedule integrity, exact-path analysis checks and invalid-input controls |

The frozen design is `assay_frontier/PROTOCOL.json`. All simulation values are generated under its declared mathematical models. The values are not biological observations. Missing sufficient-block entries denote a nonpositive guaranteed gap, not a failed computation or proof of impossibility.
