# ChronoWitness: measured memory for retrospective calibration

This branch tests the actual E1 refit and E2-A calibration on the experimental fluorescence arrays of Lugagne, Blassick and Dunlop, Nature Communications 15, 2148 (2024), https://doi.org/10.1038/s41467-024-46361-1. Source data: https://doi.org/10.5281/zenodo.8114649, datasets.zip, CC-BY-4.0. Code follows the repository MIT license. No manuscript is included.

The E1 protocol and implementation are unchanged. All 210 E1 metric records are checked against the archived run. E2 fits raw, offset and nonnegative affine predictions using early observations in each of the three E1 evaluation experiments and assesses them on the same later windows. Both input alignments, all three horizons, five base models and three calibration cutoffs are retained: 810 metric rows and 270 calibration records. E1 outcomes were already examined; E2 is retrospective development, not another blind validation. No scientific success threshold is introduced for this resource check.

The workflow runs two CPU equivalents with a 3,000,000,000-byte cgroup memory limit and no swap. This leaves a design reserve of 1 GB relative to a 4 GB machine. Kernel memory.peak includes cache as well as processes. Process RSS and timings are reported separately. Successful execution verifies the bounded computational workload; qBraid base services, its exact CPU performance and its session controls are not measured here.

The complete dataset is downloaded remotely and checksum-verified. It is not placed in GitHub artifacts. Artifacts contain scripts' results, fitted coefficients, metrics, resource counters and Docker execution metadata. Scientific data are never generated synthetically. The pre-existing E1 index-coded software selfchecks remain unit checks, not experimental inputs.

The protocol is committed before execution. The numerical results must be interpreted separately from the memory gate. Predictive calibration does not certify FD7 e-process bias bounds or directly validate FD7 in cells.
