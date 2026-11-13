# ChronoWitness

[Castellano](README.es.md) · [FD7 leading case](docs/FD7_DEMO.md) · [Epistemic graph](https://facundofirmenich.github.io/ChronoWitness/epistemic-graph.html?lang=en) · [SuperGraph](https://facundofirmenich.github.io/ChronoWitness/supergraph.html?lang=en) · [Interactive FD7 render](https://facundofirmenich.github.io/ChronoWitness/render-fd7.html?lang=en) · [Native downloads](https://github.com/FacundoFirmenich/ChronoWitness/releases)

ChronoWitness designs matched temporal inputs to test classes of models of cellular memory. Its FD7 schedules agree on cyclic word counts through order seven and on the stated two-state periodic mean identity. The exact witnesses show where readers with more states can distinguish the histories. The observation and inference contracts specify how a measured contrast can bear on that distinction.

![Exact FD7 state trajectories](docs/assets/FD7_WITNESS_3D_EN.svg)

## Explore a case

The [FD7 demo](docs/FD7_DEMO.md) guides you from a certified occupation contrast of **1/24** to a one-symbol edit that produces **0** in the specified finite window. Open the render and epistemic graph in your browser, or use the bilingual [Streamlit and Docker editor](docs/FD7_DEMO.md#run-the-editor) to change an input and export the result. The [community and research guide](docs/COMMUNITY_RESEARCH.md) covers model discrimination, finite acquisition and local cellular calibration.

The [delivery evidence guide](docs/EXPOSURE_INTERFACE.md) connects the FD7 contrast to the per-arm certificates in [ExposureBounds v4.16.0](https://doi.org/10.5281/zenodo.24182710) and describes the prospective cellular evaluation.

## Start without Git

1. Download the native ZIP for your platform from Releases and extract the whole folder. Targets are Windows x64, Linux x64, and macOS for Apple Silicon or Intel. Use the target listed on the asset.
2. Open `START_HERE.bat` on Windows, `START_HERE.command` on macOS, or `START_HERE.sh` on Linux. The ChronoWitness executable in the same folder also opens the menu.
3. Type `en all` for the complete public core, `en 1,3` for a selection, or `en atlas` to explore. Results are written under `source/research/results` in a native package.

The native package bundles Python, numerical dependencies and target-specific C++ engines. The full run executes these engines and compares results with the distributed reference. The source build also checks compilation from C++17 source. Native binaries are unsigned. If your operating system does not allow them, use the source route in the [getting-started guide](docs/GETTING_STARTED.md).

Local development used a mid-range **2016 laptop** with an Intel i5-6200U and 8–16 GB DDR3 RAM. The larger campaigns also used hosted CPU resources. [Native v0.15.0 and platform receipts](https://github.com/FacundoFirmenich/ChronoWitness/releases/tag/v0.15.0)

| Block | Scope |
|---|---|
| 1 | Exact reader identities, phase balance, and reader/instrument checks |
| 2 | Finite reporting, delivery bounds, sequential inference, counts, and kinetic witness |
| 3 | Certified design margin, exact power, worked example, and controls |
| 4 | Frozen trajectory assay, Monte Carlo checks against independent references, and application interfaces |
| all | Complete public core and reference verification |
| atlas | Offline evidence map, guided reading, typed dependencies, and the exact FD7 trajectories |

## Inspect the results and their scope

- [Exact structure and thresholds](docs/SCIENTIFIC_RESULTS.md), [worked example](docs/WORKED_EXAMPLE.md) and [literature context](docs/LITERATURE_CONTEXT.md).
- [Observation contract](docs/ASSAY_GUIDE.md), [trajectory assay](docs/TRAJECTORY_ASSAY.md) and [figure reproduction](docs/FIGURE_REPRODUCTION.md).
- [Observed cellular calibration](docs/CELLULAR_OBSERVATIONS.md), [frozen prediction E9](research/e9-execution/E9_NUMERICAL_PROTOCOL.json), [transport E10](research/e10-transport/README.md), and [reserved acquisitions E11](research/e11-causal/README.md).

The cellular studies preserve local tail deterioration and unsupported jurisdictions. Their published input programs are different from a paired FD7/FD8 intervention. The native core reproduces the certificates and the assay simulations. The separate acquisition studies specify their own sources, prerequisites and computation.

The atlas distinguishes a reading sequence from scientific dependencies. In the argument view you can inspect all premises of a conjunction. The 3D witness shows phase, arm and reader state. Its exact state-3 occupation contrast is 1/24.

## Source route and citation

Use `Start-Windows.bat`, `Start-macOS.command` or `start-linux.sh` with Python 3.12 for the source menu. The complete source run starts with `python launch.py --mode full`. The root `Dockerfile` builds the reproduction container, while `Dockerfile.streamlit` serves the interactive editor. [Reproduction guide](docs/GETTING_STARTED.md)

[Contributing](CONTRIBUTING.md) · [Issues](https://github.com/FacundoFirmenich/ChronoWitness/issues) · [Discussions](https://github.com/FacundoFirmenich/ChronoWitness/discussions)

Facundo Firmenich, Pau Firmenich and León Firmenich. [Citation metadata](CITATION.cff) · [Archived v0.14.3 software](https://doi.org/10.5281/zenodo.24147203) · [All versions](https://doi.org/10.5281/zenodo.24117387). The DOI refers to the named archived version. The original code is [MIT licensed](LICENSE).
