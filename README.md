# ChronoWitness

Exact temporal-input identities and kinetic-reader certificates.

Research and software by **Facundo Firmenich**. Version **0.10.0**.

ChronoWitness studies how finite-state and molecular readers distinguish periodic input histories. It provides exact computations for a fixed pair of binary schedules, FD7, and connects state thresholds to integrated kinetic occupations, finite observation, delivery errors, count saturation and statistical testing.

## Scientific contents

| Component | Reproduced result |
|---|---|
| Temporal design | Matched cyclic word counts through order seven, run multisets and autocorrelations |
| Finite-state readers | Deterministic minimum four under the phase-balanced profile-law contract; positive discrete Markov minimum three |
| Kinetic readers | A continuous-time three-state construction, independently certified integrated occupations and a quantified rate-perturbation neighborhood |
| Observation | Finite-window reporter corrections, delivered-input error bounds and saturation envelopes |
| Molecular counts | Explicit mRNA–protein moment bounds, retaining correlations and degradation |
| Inference | Exact checks of block-level tests valid under optional stopping |

The calculations evaluate declared mathematical models. The witness margins are model quantities; assay power depends on experimental calibration and variability.

## Reproduce

Use Linux, Python 3.10 or newer and a C++17 compiler. The scientific computations use the Python standard library.

```sh
cd research
python reproduce.py
python finite_reporter/verify.py
python input_robustness/verify.py
python statistical_inference/verify.py
python count_tails/verify.py
python translation_counts/verify.py
python supplement-v08/build_supplement.py
python kinetic_reader/verify.py
cd ..
python verify_release.py
```

The GitHub Actions workflow runs this full sequence. `verify_release.py` checks every distributed file and compares fresh results with the archived mathematical certificates. New computation goes into `research/results/`.

## Data and implementation

Data S1–S9 retain `research/supplement-v08/data/`, Data S10 retains `research/supplement-v09/data/`, and Data S11 is in `research/supplement-v010/data/`. The directory versions identify unchanged dependencies. The [data dictionary](research/supplement-v010/DATA_DICTIONARY.md) explains their columns and normalization. `expected/core/` contains reference outputs for independent regression.

The kinetic implementation uses exact rational spectral propagation and a separate uniformization implementation with outward-rounded intervals and explicit truncation bounds. Its independent periodic distribution calculation uses a three-state tree formula.

## Release and citation

The latest release contains this complete code-and-data distribution, its checksum and citation metadata. `CITATION.cff` and `.zenodo.json` describe the software for the GitHub–Zenodo integration. The Zenodo DOI will be added when assigned.

The manuscript and its Supplementary Information document are held separately until their bioRxiv release. This repository and its release assets contain the reproducible software and mathematical data.

## License

The software is licensed under **GNU General Public License version 3 only**, SPDX **GPL-3.0-only**. See [LICENSE](LICENSE). This choice does not license or publish the separately held manuscripts. The included numerical tables and certificates are the mathematical outputs used by the software.
