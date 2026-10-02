# Audit

Dated log of editorial passes and verification runs. Newest first.
See the workspace docs (run `papers docs`): writing-pipeline.md §7 and refresh-pipeline.md.

## 2026-10-02 — initial publication

Scope: first publication of the paper from the origin conversation (chats/, not committed).
Changes:
  - brief, research log and frozen bibliography (76 references resolved through doi.org on 2026-10-02)
  - simulation/: estimators R, Q, T, S on a linear-Gaussian VAR; estimator checks; dissociation atlas; 1000-network
    ensemble; six controller sweeps; conjunctive-test statistics (margins, PCI anchor, label noise, Clopper-Pearson
    sample sizes, design effect, McNemar power, order-statistic nulls); 20 internal checks
  - PAPER.md with Propositions 1 to 3, four figures, one table and the MCR-1 design
Verification:
  - run: verification/model.json PASS (20/20 checks)
  - voice: OK (0 errors, 0 warns)
  - refs: 76 cited, 76 entries, PASS
  - claims: 148 bound (104 computation), PASS
  - build: 22 pages, no missing-character warnings

<!--
## YYYY-MM-DD — <pass name>
Scope: <the bounded list of changes>
Changes:
  - ...
Verification:
  - voice: <errors / warns>
  - refs: <missing / unused>
  - claims: <reconciliation result>
  - build: <pages, missing-char warnings>
  - check => PASS/FAIL
-->
