# Calibration transport: E3-A

E3 asks whether an early temporal validation segment can select a calibration that remains useful in a later segment, with the uncorrected predictor retained as an explicit option. The study uses published cellular measurements; it does not administer FD7 to cells.

The three history predictors preserve the original E1 features and regularization grid. Training-experiment predictions exclude that experiment from all base-model fitting and use nested, experiment-grouped regularization selection. A single decision threshold is learned from the four original training experiments in the primary configuration. The three original test experiments have already been inspected in E1/E2: evaluation on them is retrospective development, not a new blind confirmation.

`PROTOCOL.json` fixes time windows, decision candidates, threshold selection, sensitivity analyses and failure policy before this E3 execution. `e3.py` retains all 126 experiment/model/alignment/horizon cases, 630 policy metrics and time-stratified results, including deterioration. It independently checks that the unchanged raw/static-correction cases reproduce E2.

Run `python e3.py /path/to/verified/datasets.zip` with Python 3.12, NumPy 2.2.6 and SciPy 1.15.3. The source package includes the unchanged E1 module/protocol and reference results. Download the source data only in the remote compute environment. The MIT code license does not replace the original dataset's CC-BY-4.0 license.

No threshold is replaced after seeing test results. An uncorrected winner or failed transport is a valid outcome of this study.
