# From temporal identity to an assay plan

ChronoWitness separates three design questions: which model predicts equal responses, which observable preserves that equality, and how much data can resolve a qualified contrast. The trajectory study connects them for two explicitly declared kinetic models.

## What the new study resolves

The two-state model has zero periodic occupation contrast. Nevertheless, initializing a slow reporter at zero produces a one-period raw contrast of 0.0174473. The certified three-state reader has positive occupation contrast near 0.01007947, but its raw slow-reporter contrast is negative. Endpoint correction restores the integrated-state target on each simulated path.

These results make acquisition design consequential. At 8,192 independent paired blocks, zero tolerance and the original four-stake test, estimated power is 0.5605 for one-period windows and 0.9980 for four-period windows. Each estimate uses 512 experiments; Data S13 supplies binomial uncertainty intervals and both seed counts. Four-period blocks cost four times as much observation time. At equal accumulated time, the available comparison is 0.2090 for 1,024 four-period blocks versus 0.2715 for 4,096 one-period blocks, with overlapping pointwise intervals. A longer window is therefore not automatically a more efficient assay.

The calibration calculation uses qualified rate intervals and endpoint error bounds. If each paired score can differ from its ideal value by at most b, the test needs null allowance b and range 1+b. An ideal alternative margin D guarantees separation only above D-2b. The complete 48-case rational grid retains 28 positive worst-case gaps and 20 cases requiring tighter bounds or a changed acquisition design for that guarantee.

## Export an explicit stimulus plan

From the repository root:

```sh
python research/application/plan.py --blocks 24 --pulse-duration 1 --unit dimensionless --periods 4 --burn-in-periods 1 --seed 20261110 --out fd7-plan.csv
```

The CSV contains every pulse in both arms, randomized within-pair assignment and a shared uniform cyclic phase. Metadata records the seed and file hash. This is an abstract plan; it does not operate hardware. Set the time unit, input levels and wash-in using a qualified biological system. The example values are declared planning choices, not measurements or a calibrated biological protocol.

## Analyze qualified observed blocks

Supply a CSV with columns `block_id,score,mean_tolerance,support_radius`. Each row must represent the declared assignment block. Tolerances and support bounds must be fixed or predictable before its outcome. Then run:

```sh
python research/application/analyze.py observed-blocks.csv --mixture four --alpha 0.05 --out sequential-analysis.json
```

The analyzer rejects duplicate block IDs, nonfinite entries and scores outside their declared support. It records the evidence trajectory and first threshold crossing. A value entered in a CSV is not itself a calibration certificate: the assay record must justify the range, conditional mean allowance, pairing and sampling assumptions.

## Reproduce the trajectory study

```sh
python -m pip install -r requirements-assay.txt
python research/assay_frontier/run.py
python research/application/verify.py
```

Run on Linux with Python 3.12 and a C++17 compiler. The campaign reads the distributed certified generator and exact-power references. Its frozen protocol specifies all models, seeds, windows, tolerances, horizons and checks. It uses event-driven continuous-time paths, independently calculated moments, four exact first-crossing benchmarks and fresh trajectories for every power-study block. It does not resample a finite simulated pool. Results include all 72 settings, pointwise and simultaneous intervals, null cases and both betting mixtures.

The bounded reporter isolates acquisition and correction effects. Chemical counting noise, cell division, photobleaching and device-specific variability require an observation model fitted or bounded for the selected assay. Existing count-envelope modules supply a separate route for qualifying unbounded molecular counts and saturation.

## Qualify a biological application

Record the biological reader and actuator; delivered-input traces by arm; reporter channels and parameter bounds; endpoint precision and saturation; pairing, batches and experimental units; and the predeclared inferential rule. Use independent pilot information to qualify viability, drift, wash-in and detector behavior before the confirmatory comparison. [Literature context](LITERATURE_CONTEXT.md) connects these tasks to programmable stimulation and feedback platforms.
