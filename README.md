# ChronoWitness

**Temporal input design for testing models of cellular memory.**

ChronoWitness turns carefully matched input histories into quantitative tests of dynamical models. Its FD7 schedules share the same symbol counts, short-word statistics, run lengths and autocorrelations. Within the two-state promoter class, they must produce the same periodic mean response for every admissible choice of switching rates. A measured difference can therefore challenge that model class once delivery, observation and sampling have been accounted for.

The software connects that identity to exact state thresholds, kinetic constructions, reporter dynamics and sequential inference. Every reported computational result is accompanied by a reproducible calculation or certificate.

```mermaid
flowchart LR
    A[Matched temporal inputs] --> B[Parameter-uniform model identity]
    B --> C[Acquisition and detector budget]
    C --> D[Block-level statistical test]
    E[Separating kinetic models] --> F[Certified contrast]
    F --> C
```

## Start with the scientific example

From a checkout of this repository:

```sh
python research/design_frontier/tutorial.py
```

The example verifies the two-state polynomial identity, evaluates a kinetic promoter exactly, transports its mean through a linear reporter, and reads the certified three-state contrast. It then connects an explicitly defined observation model to a conservative sample-size calculation. It uses the Python standard library and requires no experimental dataset.

Continue with the [worked example and assay guide](docs/WORKED_EXAMPLE.md), or inspect the [results and their assumptions](docs/SCIENTIFIC_RESULTS.md).

## What the method establishes

| Question | Result |
|---|---|
| Can matched short-word statistics hide a temporal distinction? | FD7 matches cyclic word counts through order seven while retaining a reader-dependent distinction. |
| How many deterministic states are needed? | Four, for the phase-balanced occupation-profile law used here. |
| How many positive Markov or kinetic states are needed? | Three; all two-state readers in the stated occupation classes share the null. |
| Does reporter dynamics preserve the null? | A common stable linear cascade preserves periodic mean equality. Finite windows admit endpoint corrections or transient bounds. |
| Can acquisition and detection change the contrast? | Delivery errors, hidden endpoints and saturation enter an explicit observation budget. |
| Can an experiment stop when evidence is sufficient? | The bounded-block test supports optional stopping under its conditional range and mean contracts. |

The design study also searches a fixed positive-generator domain and certifies the selected rational candidate independently. [Data S12](research/supplement-v011/data/) contains the search record, interval certificate and exact power calculations. These distinguish the existence of a separator, the size of its contrast and the performance of a specified statistical design.

## Design the observation as well as the input

The [trajectory assay study](docs/TRAJECTORY_ASSAY.md) connects continuous-time readers, finite reporter windows and sequential power. It shows how a reporter transient can create a raw contrast under the two-state null or reverse a separating contrast. Endpoint correction and a calibration budget recover a qualified comparison. Power is reported with Monte Carlo intervals and acquisition-time comparisons.

Use the same guide to export a paired FD7 stimulus plan or analyze qualified block scores. [Data S13](research/supplement-v012/data/) retains the complete declared campaign, including null cases, alternative mixtures and calibration settings that do not retain a positive guaranteed gap.

## Cellular observations and local calibration

The [external-data studies](docs/CELLULAR_OBSERVATIONS.md) evaluate how input history and early calibration transfer to later fluorescence measurements. They retain the original experimental split of a published optogenetic dataset, separate numerical fitting from retrospective development, and resolve results by temporal segment, programmed input edge and fluorescence band.

The local study identifies 270 jurisdictions with adequate calibration and evaluation support: 129 MAE gains above 1%, 141 practical ties and no losses above that tolerance under early selection. Its fixed-composition comparator gains more often but also loses in 41 jurisdictions. Upper-tail error worsens in 31 supported jurisdictions under selection. The full record includes 378 jurisdictions without sufficient support for the local-calibration conclusion.

These results qualify observation and calibration. The source dataset used its own input programs and does not constitute a paired FD7 intervention. [Inspect all local results and reproduce E4](research/e4-local/README.md).

## New frontier: nested evidence and extended input identities

The [E6–E8 and FD8 campaign](research/e6-e8-fd8/README.md) adds ten acquisition dates and a certified 32-pulse extension. The early guard reduces local upper-tail losses from 102 to 62 on the same 552 supported jurisdictions, while retaining adverse transfers and non-estimable strata. These overlapping jurisdictions are not independent replicates.

The FD8-32 pair preserves the three-state deterministic profile-law null and yields a 60.33% larger contrast for the same kinetic witness at fixed total period, using shorter pulses. A separate phase-law check demonstrates why equal means alone are insufficient. The input audit of the cellular acquisitions does not establish a direct FD7 intervention.

Full source, residual-level results and exact certificates are distributed in [release v0.14.0](https://github.com/FacundoFirmenich/ChronoWitness/releases/tag/v0.14.0). Earlier campaigns remain unchanged and retain their original scope.

## Reproduce the results

The complete verification runs on Linux with Python 3.12 and a C++17 compiler:

```sh
python -m pip install -r requirements-assay.txt
python reproduce_release.py
```

This command rebuilds the mathematical results, checks the interval certificate, exact first-crossing probabilities and trajectory-level Monte Carlo against independent moment references, and compares the outputs with the distributed references. The [GitHub Actions workflow](.github/workflows/reproduce.yml) executes the same procedure.

The numerical search is a separate, reproducible step:

```sh
python -m pip install -r requirements-search.txt
python research/design_frontier/search.py
```

Its protocol fixes the parameter domain, objective, seeds and evaluation budget. Numerical proposals are assessed by rational interval certification. The search record includes termination status for every seed.

## Choose a route through the repository

- **Understand the method:** [scientific results](docs/SCIENTIFIC_RESULTS.md) and [worked example](docs/WORKED_EXAMPLE.md).
- **Design an observation:** [assay requirements and decision path](docs/ASSAY_GUIDE.md).
- **Inspect the evidence:** [data dictionary](research/supplement-v010/DATA_DICTIONARY.md), Data S1–S11 in their versioned directories, [Data S12](research/supplement-v011/data/) and [Data S13](research/supplement-v012/data/).
- **Extend the calculation:** exact reader code in `research/analysis/`, observation bounds in `research/finite_reporter/` and `research/input_robustness/`, count envelopes in `research/count_tails/` and `research/translation_counts/`, and tests in `research/statistical_inference/`.
- **Audit a release:** `RELEASE_MANIFEST.json` records file hashes; release assets include the source distribution and its checksum.

The repository supplies theoretical and computational research, including secondary analysis of published cellular measurements. Applying the test to cells requires the assay-specific rates or bounds, observation model and experimental units described in the guide.

## Cite and reuse

Research and software by **Facundo Firmenich**. Citation metadata is available in [CITATION.cff](CITATION.cff); release metadata is supplied for GitHub–Zenodo archiving.

The code is distributed under the **MIT License**. See [LICENSE](LICENSE). The academic manuscript and supplementary document are maintained separately.
