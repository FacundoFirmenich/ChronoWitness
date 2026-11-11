# Local calibration transport in cellular time series

This study asks where an early calibration decision transfers to later observations. Jurisdictions combine experiment, temporal segment, programmed input transition and training-defined fluorescence band, separately for each forecast horizon and alignment.

The frozen design produces 648 jurisdictions and 5,184 metric rows. Evaluation support is adequate in 497 jurisdictions; 270 also support local calibration. On those 270, early local selection produces 129 MAE gains above 1%, 141 practical ties and no losses above 1%. The fixed equal-weight comparator produces 170 gains, 41 losses and 59 ties on the same observations. Upper-tail mean error increases under local selection in 31 supported jurisdictions. Full continuous changes, support failures and sensitivity thresholds are retained.

These are retrospective, dependent comparisons on published cell measurements. The 227 evaluation-supported contexts with insufficient calibration support remain OUT_OF_SUPPORT; 151 evaluation-unsupported jurisdictions remain NOT_ESTIMABLE. The raw-prediction fallback is not evidence of successful calibration. Input transitions are program edges, not inferred molecular connections. The dataset does not contain paired FD7 interventions.

## Reproduce

Extract REMOTE_E4.zip into a fresh directory. It contains the predictor coefficients, inherited comparator decisions, benchmark module and frozen protocol. Install Python 3.12, numpy==2.2.6 and scipy==1.15.3. Set OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1 and MKL_NUM_THREADS=1.

Download datasets.zip from https://zenodo.org/api/records/8114649/files/datasets.zip/content. Verify the SHA-256 in PROTOCOL.json. Run `python e4.py /absolute/path/to/datasets.zip` in a fresh copy without an existing results directory. The original output directory must be preserved as the reference, not overwritten.

Source: Lugagne, Blassick and Dunlop, Nature Communications 15:2148 (2024), https://doi.org/10.1038/s41467-024-46361-1. Data license CC-BY-4.0; project code MIT.

VERIFICATION.json records full archive readback, frozen-source equality, reconstruction of early decisions and exact partition checks. CPU Colab execution completed in 63.43 seconds including environment preparation and remote data retrieval; the scientific subprocess took 10.54 seconds. These durations are observed run times, not a billing claim.
