# Brief

## Question

The origin material is a long conversation about the biological and dynamical basis of consciousness. It moves through criticality, oscillations and travelling waves, the thalamus, dendrites, mitochondria, glia, breathing, development and selfhood, and converges on one object: a "minimal conscious regime" defined by four invariants (recurrent causation, perturbational repertoire, temporal depth, stable multiscale organization). Everything else (criticality, rhythms, thalamic drive, metabolism) becomes a controller that moves a system into or out of the regime, and self-related capacities (bodily self, perspective, metacognition) form a separate profile. It ends with a flagship anaesthesia experiment (MCR-1) and six kill criteria, and its own assessment is that the four invariants have no formal estimators, that nothing shows they are non-redundant, and that the statistics of testing a four-way conjunction were never worked out. So: can the four invariants be given estimators on one model class, can each fail while the other three hold, what does a conjunctive test cost in sensitivity, sample size and power, and what experiment follows from those numbers?

## Claim

Results about a stated model class (linear-Gaussian vector autoregressions on a parcellated network), each proved or computed and checked numerically.

1. Estimators. R (between-region return energy over out-of-region energy) is zero for every region-acyclic operator and positive for nonnegative operators with a returning path. Q (share of the response leaving the pulsed region times the dissimilarity of responses to different regions) is threshold-free and vanishes for local and for stereotyped responses. T (lagged mutual information summed over lags, conditioned on the input path) depends on the operator alone, so a fast network buffering a slow input scores near zero. S (test-retest overlap of the slowest dynamically independent macro) rests on a characterization: for a VAR(1) with nonsingular innovations, a linear macro has zero dynamical dependence if and only if its row space is invariant under the transposed operator.
2. Non-redundancy. Four families of modular networks each fail one invariant and pass the other three over an interval of pass thresholds, robustly across seeds; in a random ensemble a sizeable share of networks that pass three invariants fail the fourth.
3. Controllers. Single parameter sweeps (feedback scale, between-region coupling, all-to-all coupling, region-mean coupling, equal-rate mixing, spectral radius) move one or two invariants; none moves Q alone.
4. Statistics of a conjunctive test. Per-invariant margin for 90% joint sensitivity (independent and correlated errors), the PCI anchor in minimally conscious patients, bias from label noise, exact Clopper–Pearson sample sizes with a design effect, McNemar power for necessity tests, and order-statistic nulls for transition timing.
5. A revised MCR-1 with the corrected timing prediction (loss at the first failure, recovery at the last), its endpoints and its kill criteria.

## Kind

Formal-model. has_simulation: true; claims bound in claims.yaml to simulation/output/results.json through a recorded run.

## Cornerstone literature

Perturbational complexity and anaesthesia (Massimini et al.; Casali et al.; Casarotto et al.; Sarasso et al.; Comolatti et al.). Experience during unresponsiveness (Radek et al.; Sikka et al.; Siclari et al.). Global states as multidimensional (Bayne, Hohwy and Owen; Birch, Schnell and Clayton; Bayne et al. on C-tests). Recurrence and feedback (Lamme; Suzuki and Larkum; Aru, Suzuki and Larkum; Redinbaugh et al.). Integration and differentiation (Tononi and Edelman). Criticality (Beggs and Plenz; Priesemann et al.; Wilting and Priesemann; O'Byrne and Jerbi; Touboul and Destexhe; Tagliazucchi et al.; Maschke et al.; Algom and Shriki). Emergence and dynamical independence (Barnett and Seth; Rosas et al.; Milinkovic et al.). Thalamus (Whyte et al.; Bastos et al.; Luppi et al.; Huang et al.). Rhythms and waves (Buzsáki and Draguhn; Fries; Lundqvist et al.; Muller et al.; Cruddas et al.). Metabolism, glia and breathing (Sandi et al.; Rodriguez et al.; Zhao et al.; Zhou et al.; Tort et al.). Self-related capacities (Blanke; Serino et al.; Fleming; Gardier and Geurten; Bayne et al. on infants; Passos-Ferreira). Theories (Dehaene and Changeux; Mashour et al.; Brown, Lau and LeDoux; Seth and Bayne; Storm et al.; Cogitate Consortium). Biological naturalism (Seth; Kleiner; Lane). Statistics (Clopper and Pearson; McNemar; Rogan and Gladen; Dunnett and Sobel; Kish; David and Nagaraja).

## Discipline

The paper does not claim that the four invariants are the necessary conditions of consciousness; it makes that hypothesis measurable and states what its test costs. No claim about artificial systems, organoids or animals beyond what cited sources report. Unverified items in the origin material (preprints cited as established, some author attributions) are not used; the conversation's own self-reports and recaps are dropped. No number in the manuscript that is not bound to a JSON pointer in a recorded execution or to a checked source.
