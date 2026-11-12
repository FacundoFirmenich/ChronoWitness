# Literature context

[Castellano](CONTEXTO_BIBLIOGRAFICO.md)

ChronoWitness complements parameter-estimation and stimulus-design methods with a parameter-uniform reference for a specified class of periodic readers. The distinction concerns the statistical target: it does not remove the need to qualify the physical observation.

| Research contribution | Connection to ChronoWitness |
|---|---|
| [Apgar et al., stimulus design](https://doi.org/10.1371/journal.pcbi.0040030) and [Mélykúti et al., model discrimination](https://doi.org/10.1186/1752-0509-4-38) | Design informative perturbations for rival models; FD7 supplies an exact shared prediction within its null class. |
| [Ruess et al., iterative experiment design](https://doi.org/10.1073/pnas.1423947112) and [Rullan et al., single-cell interrogation](https://doi.org/10.1016/j.molcel.2018.04.012) | Connect light stimulation, measurement and system identification; their approach can inform assay-specific calibration. |
| [Balleza et al., reporter maturation](https://doi.org/10.1038/nmeth.4509) | Reporter response depends on the selected protein and conditions. The endpoint criterion identifies which measured channels or bounds are needed. |
| [optoPlate-96](https://doi.org/10.1038/s41596-019-0178-y), [LITOS](https://doi.org/10.1038/s41598-022-17312-x) and [optoPlateReader](https://doi.org/10.1038/s42003-023-05532-4) | Demonstrate programmable illumination and, for optoPlateReader, integrated readout and feedback. FD7 compatibility remains an assay-specific qualification task. |
| [Gillespie, event-driven simulation](https://doi.org/10.1021/j100540a008) | Underpins the jump-process sampling used for the declared kinetic models. |
| [Morris et al., simulation-study design](https://doi.org/10.1002/sim.8086) | Motivates explicit aims, models, estimands, methods, performance measures and Monte Carlo uncertainty. |
| [Clopper and Pearson, binomial intervals](https://doi.org/10.2307/2331986) | Quantifies Monte Carlo uncertainty in first-crossing proportions; simultaneous intervals use Bonferroni allocation. |

This is targeted primary-source contextualization. It does not establish hardware integration, measured biological power or an exhaustive priority assessment. The simulation study and prospective application specification are described in the [trajectory assay guide](TRAJECTORY_ASSAY.md).


## Contemporary experimental context

[Cell-in-the-loop pattern formation (2020)](https://doi.org/10.1038/s41467-020-15166-3) combines living cells with computed signalling. [Temporal MAPK/ERK transmission (2023)](https://doi.org/10.1371/journal.pcbi.1011155) supplies a primary experimental reference and the data used in the external-data studies. [Deep model predictive control (2024)](https://doi.org/10.1038/s41467-024-46361-1) demonstrates feedback control across thousands of single cells. [CytoTape (2026)](https://doi.org/10.1038/s41586-026-10156-9) extends recording of gene-regulatory dynamics across weeks.

These technologies and studies address distinct observational and control targets. ChronoWitness contributes exact temporal-input identities and explicit inferential conditions for a specified reader class. Hardware integration and validation of the paired FD7/FD8 intervention remain separate tasks. See the [53-reference bibliography](REFERENCES.md).
