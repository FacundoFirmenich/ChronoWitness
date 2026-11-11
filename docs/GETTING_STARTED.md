# Getting started

Download the source ZIP from the latest release, extract it, and keep the folder intact. You do not need Git or an account. Code: MIT; external datasets keep their original licences.

## Standalone desktop example

The release assets include platform-specific `ChronoWitness-<system>-<architecture>.zip` packages. Extract the archive and run `ChronoWitness` (`ChronoWitness.exe` on Windows). These bundles include their own Python runtime. They run the exact example and open a persistent HTML result; no scientific-package installation or account is needed. The complete campaign uses the Docker route below. Bundles are unsigned; if the operating system blocks them, use the source route rather than disabling security.

## A first result from source, without installing scientific packages

Install Python 3.12 from https://www.python.org/downloads/ if it is not already installed. On Windows select “Add Python to PATH”.

| System | Start the exact worked example |
|---|---|
| Windows | Double-click `Start-Windows.cmd` |
| macOS | In Terminal, run `sh Start-macOS.command`; a Git checkout also preserves its executable permission |
| Linux | In Terminal, run `sh start-linux.sh` |

Equivalent on every system: `python launch.py` (or `python3 launch.py`). The example needs only the standard library and writes `research/results/DESIGN_TUTORIAL.json`. Success is `PASS_EXACT_TUTORIAL`. This checks exact mathematics; it does not simulate a new cellular experiment.

## Complete core reproduction

Install and start [Docker Desktop](https://docs.docker.com/desktop/) on Windows/macOS or [Docker Engine](https://docs.docker.com/engine/install/) on Linux. Run `python launch.py --mode full`. This builds an isolated Linux/amd64 environment, compiles the C++ routines, reproduces the core certificates, assay and power calculations, and compares 46 reference outputs. Internet is needed for the first build. Apple Silicon uses amd64 emulation for the same numerical toolchain and may be slower. This is a container route, not a signed standalone native executable.

The verified Linux reference previously took about five minutes for scientific computation; installation, emulation and hardware change this. Allow 4 GB RAM and several GB free disk for Docker. No GPU, payment, credentials or Drive mount is required. Output stays in `research/results/`; `PUBLIC_VERIFICATION.json` must report `PASS_PUBLIC_CODE_DATA_REPRODUCTION`. A nonzero exit is a failure, not a partial pass.

`python launch.py --mode doctor` reports prerequisites without changing your machine. `--mode graph` opens the offline epistemic map. If macOS security blocks double-clicking a downloaded script, use the documented Terminal command; do not disable system protections.

## Scope and data

The full core route does not rerun every external-cell campaign. E1–E11 have separate input datasets, acquisition protocols and resource needs, linked in [the evidence ledger](EVIDENCE_LEDGER.json). E11 is the latest public cellular analysis. E12 remains private retrospective development. New records require their own protocol; rerunning an exposed reserve does not create a new holdout.

