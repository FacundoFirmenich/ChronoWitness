# Getting started

[Guía completa en castellano](GUIA_ES.md) · [Evidence atlas](https://facundofirmenich.github.io/ChronoWitness/?lang=en)

## Native package

Download the target archive and extract every file. Use the START_HERE script or open the ChronoWitness executable in the extracted folder. Choose language and scope in one prompt: `en all` runs the complete public core, `en 1,3` runs selected blocks, and `en atlas` opens the offline atlas.

The native package includes Python, numerical dependencies and the C++ engines built on the target platform. The complete run compares fresh results with the published references. Results are written under `source/research/results`. The run receipt lists the files produced during that run. The binary is unsigned. If your operating system blocks it, use the source route below.

| Block | Contents |
|---|---|
| 1 | Exact phase-balanced reader identities, stochastic readers and instrument checks |
| 2 | Finite reporting, delivery, sequential inference, count envelopes and kinetic witness |
| 3 | Certified design, exact power, worked example and controls |
| 4 | Frozen trajectory assay, Monte Carlo verification and application interfaces |
| all | The public core, regenerated and compared with distributed results |
| atlas | Bilingual offline evidence map, arguments, guided routes and FD7 witness |

## Source package

Install Python 3.12 if needed. From the extracted source archive run `Start-Windows.bat`, `Start-macOS.command` or `sh start-linux.sh`. To select without the menu, run `python workbench.py --lang en --blocks example` or `python workbench.py --lang en --blocks 2,3`.

For the complete source reproduction, run Docker and select `en all`, or run `python launch.py --mode full`. This recompiles the C++17 engines in the container. Direct reproduction from source needs a C++17 compiler and the dependencies in `requirements-assay.txt`. The external acquisition campaigns have separate data and compute requirements in their own protocols.

## Read the evidence

Use the [scientific results](SCIENTIFIC_RESULTS.md), [assay guide](ASSAY_GUIDE.md), [worked example](WORKED_EXAMPLE.md) and [trajectory assay](TRAJECTORY_ASSAY.md) for detailed derivations. The [cellular calibration record](CELLULAR_OBSERVATIONS.md) preserves adverse local outcomes. A native calculation reproduces mathematical or computational evidence for the declared protocols. The cellular records are secondary observations under their published input schedules.

The atlas has a spatial map and a dependency view. A guided tour chooses reading order. Scientific arrows represent typed relations, and conjunctions retain all required premises. Audit view gives the source hash. The witness view projects the exact FD7 phase, state and arm data. It reports state-3 occupation 3/24 for A and 2/24 for B. The arm axis is categorical.

Generate the figures from a Python environment with the figure dependencies using `python tools/render_witness_3d.py --formats svg pdf png --output figures`. See [figure reproduction](FIGURE_REPRODUCTION.md) for the earlier figures.
