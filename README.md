# The Minimal Conscious Regime

Estimators for Four Dynamical Invariants and the Statistics of Testing Them Jointly.

Indices of conscious state each track one property of brain dynamics, yet the states they must sort differ along several: under ketamine people are unresponsive and dream, under xenon the cortex answers a magnetic pulse with a large stereotyped wave, and under propofol with a small local one. We state a minimal conscious regime as the conjunction of four dynamical invariants, between-region recurrence ($R$), perturbational repertoire ($Q$), endogenous temporal depth ($T$) and stable macrostructure ($S$), and give each an estimator on a fitted linear-Gaussian vector autoregression. $R$ is zero whenever no causal path returns to its region of origin. $T$ sums lagged mutual information given the input, so a fast network that buffers a slow stimulus scores near zero. $S$ is the test-retest stability of a dynamically independent macro, and for this model class those macros are the invariant subspaces of the transposed operator. Four families of modular networks each fail one invariant and pass the other three for every pass threshold between 0.076 and 0.645 of a reference network, so no invariant follows from the other three. Across 1000 random networks, between 5.5% and 50.1% of the networks that pass three invariants fail the fourth, and none of six control parameters takes $Q$ below threshold on its own. A conjunction pays for its specificity in sensitivity: four independent invariants each need a margin of 1.94 measurement standard deviations to reach 90% joint sensitivity, against 1.28 for one, and four tests at the 94.7% sensitivity that the perturbational complexity index reached in minimally conscious patients would jointly detect 80.6%. When transition times are noisy and nothing leads anything, the first of four invariants to fail precedes the change in report with probability 0.8, so timing tests need order-statistic nulls. From these results we specify a crossover experiment with propofol, ketamine and dexmedetomidine: its endpoints, its sample size, which holds at 40 participants only while at most 4% of experience labels are wrong, and the outcomes that would refute the regime.

## Build

```bash
uv run build.py          # -> paper/PAPER.pdf  (vendored canonical recipe)
```

Requires `pandoc` and `xelatex` on PATH. From the workspace you can also run `papers build the-minimal-conscious-regime`.

## Simulation

```bash
cd simulation && uv run run_all.py   # -> output/results.json and output/figures/*.png, 20 checks
```

Part of [piatra-papers](https://github.com/piatra-institute). See the workspace docs for the research and writing pipelines.
