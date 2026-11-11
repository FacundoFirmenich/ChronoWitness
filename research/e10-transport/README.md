# E10 · Temporal transport and local risk

E10 evaluates the frozen E9 models and policies on 36 files from two additional acquisitions, with stimulation clocks of 5, 7, 20 and 30 minutes. It retains 216 file–horizon–alignment contexts. The subsequent audit reconstructs metrics from residuals, checks protection decisions and verifies the exact decomposition of squared-error changes.

The transport units are two acquisition dates, not 216 independent replicates. Fields and stimulation clocks from one date may share cells or acquisition segments. This is retrospective evaluation within the same laboratory, using input programs other than FD7/FD8.

## Reproduction on Colab CPU

Required files: `e9_core.py`, `MODEL_SELECTION.json`, `E9_NUMERICAL_PROTOCOL.json`, `E10_COHORT.json`, `E10_PROTOCOL.json`, `run_e10.py` and `analyze_e10.py`. The complete coefficients are distributed; no model is refitted. The protocol records SHA-256 hashes of the coefficients and inherited protocol.

Create the input archive in the directory containing these files:

```python
import zipfile
names = ['e9_core.py', 'MODEL_SELECTION.json', 'E9_NUMERICAL_PROTOCOL.json',
         'E10_COHORT.json', 'E10_PROTOCOL.json']
with zipfile.ZipFile('E10_INPUTS.zip', 'x', zipfile.ZIP_DEFLATED) as z:
    for name in names:
        z.write(name, name)
```

Copy the archive and both execution scripts to `/content` in Colab. Run `python /content/run_e10.py`. After COMPLETE, run `python /content/analyze_e10.py`; the latter requires NumPy, pandas and matplotlib. `COMPLETE.json` records the versions actually used. The original source is downloaded directly from Zenodo and admitted only when its size and SHA-256 match the protocol. Outputs are written to `/content/chronowitness-e10-20261111`.

Use a fresh runtime or a separately isolated directory for each reproduction. Do not mix campaign outputs. The scripts do not mount Drive. The historical custody operation used an authenticated connector and complete remote-byte verification; that custody receipt is separate from scientific execution.

## Evidence and retained distinctions

`SCHEMA_AUDIT.json` identifies admitted inputs. `SUPPORT.json` retains windows by stage and context. Residual records retain cell and time identity, observable, target, jurisdiction and each method's error. Cell-level decisions retain early support, correction, validation metrics and acceptance. `VERIFICATION.json` checks reconstruction; it does not assert an independent second model fit.

`CELL_RISK_DECOMPOSITION.csv.gz` separates incompatible correction direction from excessive correction magnitude. `NESTED_NODES.csv` retains parents, pulse/signal intersections and temporal segments, including LOW_SUPPORT. Each partition is reconstructed separately; repeated observations across partitions are not added as independent data. `THRESHOLD_SENSITIVITY.json` retains descriptive tolerances of 0%, 1% and 5%.

The archived mathematical note specifies the exact risk identity and additional conditions required for a prospective guarantee. `NEXT_RESERVE_METADATA.json` records the interval-stimulation acquisitions that were unscored at the E10 checkpoint, including an unresolved date conflict. E11 subsequently evaluates the 14 concordant acquisitions; the conflict remains unscored. Historical receipts retain their original timestamp and language.

## Attribution and licence

ChronoWitness code: MIT. Nałęcz-Jawecki and colleagues' data: [Zenodo v1.1](https://doi.org/10.5281/zenodo.7808385), CC-BY-4.0. Scientific source: [The MAPK/ERK channel capacity exceeds 6 bit/hour](https://doi.org/10.1371/journal.pcbi.1011155). Acquisition-date attribution uses commit `03f9a059d91caa2b72873e2317134ea7f7500203` of `pawelnalecz/pulsatile-information`.

MIT does not replace the original data licence. Private manuscripts and the confidential commercial annex are excluded.
