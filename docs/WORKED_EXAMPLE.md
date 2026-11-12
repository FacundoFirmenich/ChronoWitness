# An exact worked example

[Castellano](EJEMPLO_EXACTO.md)

Run `python research/design_frontier/tutorial.py` from the repository root. The program uses rational arithmetic and the distributed kinetic certificate; it does not generate observations or fit parameters.

1. **Verify FD7.** The forward polynomial construction checks equality of both symbol-conditioned two-state occupation numerators.
2. **Choose a kinetic promoter.** Equilibrium fractions are 1/4 and 3/4, relaxation rates are one and two, and pulse duration is log(2). Thus pulse contractions are exactly 1/2 and 1/4.
3. **Integrate a period.** Both schedules give the exact promoter integral `1346711/1474746 + 12 log(2)`. This particular example accompanies the all-parameter polynomial identity.
4. **Transport the mean.** A common linear reporter with synthesis/degradation gain 3/2 preserves the zero periodic contrast.
5. **Read the alternative certificate.** The positive three-state candidate has a rigorously positive integrated state-zero contrast above 0.01007947.
6. **Specify an observation law.** In the ideal example, each independent paired block samples the two arm state indicators at independent uniform times in their periodic cycles. The difference has support [-1,1] and expected value equal to the occupation contrast.
7. **Calculate a sufficient horizon.** At error level 0.05 and target power 0.8, the tutorial certifies 200,326 sufficient blocks using a conservative Hoeffding bound and rational bounds on logarithms and square roots. This is a sufficient count for the stated ideal model, not a minimum or a laboratory sample-size estimate.

For the sequential test, inspect `Data_S12_design_power.csv`. Its exact crossing probabilities concern separately declared iid scores in {-1,+1}, with specified probabilities and tolerances. The table compares finite-horizon performance of two valid mixtures; it is not a measurement of the kinetic example's biological noise.

`python research/design_frontier/controls.py` evaluates a fixed alternative input pair with the same dose, run multiset and number of switches. It loses the two-state polynomial identity. The example makes the role of the input constraints explicit.

A real experiment replaces the ideal state indicator with its measured reporter and supplies delivery, transient, detector and block assumptions through the [assay guide](ASSAY_GUIDE.md).

## Why exact counting here?

For the declared two-point score laws, capital depends only on the block count and the number of positive outcomes. Grouping equivalent prefixes makes exact first-crossing probabilities tractable. Monte Carlo is useful when a richer observation or dependence model makes this grouping impractical; its simulation uncertainty must then be quantified. The exact cases provide reference values against which a simulator can be validated.
