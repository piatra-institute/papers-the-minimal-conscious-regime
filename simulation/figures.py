"""Figures for The Minimal Conscious Regime."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyses import NAMES, FRAC, cp_power

INK, GRID, AMBER, GREEN, BLUE, GRAY, RED, PURPLE = ("#1a1a1a", "#d9d9d9", "#b45309", "#15803d",
                                                    "#2563eb", "#78716c", "#b3202c", "#7c3aed")
COL = {"R": BLUE, "Q": AMBER, "T": GREEN, "S": PURPLE}
FAM_LABEL = {"reference": "reference", "no_R": "no feedback\n(fails R)", "no_Q": "global mode\n(fails Q)",
             "no_T": "fast decay\n(fails T)", "no_S": "equal rates\n(fails S)"}


def _style(ax):
    ax.grid(True, color=GRID, lw=0.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=8)


def _title(ax, t):
    ax.set_title(t, fontsize=9.5, loc="left")


def plot_estimators(r, path):
    e = r["estimators"]
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.7))

    ax = axes[0]
    rng = np.random.default_rng(0)
    floor = 1e-4
    for i, (key, lab, c) in enumerate((("R_acyclic", "feedback removed", GRAY), ("R_cyclic", "feedback 0.3", BLUE))):
        v = np.maximum(np.array(e[key]), floor)
        ax.scatter(i + 0.12 * rng.standard_normal(len(v)), v, s=12, color=c, alpha=0.8)
    ax.set_yscale("log")
    ax.set_ylim(floor / 2, 1)
    ax.set_xticks([0, 1], ["feedback removed", "feedback scaled by 0.3"], fontsize=8)
    ax.text(0, floor * 1.6, "R = 0 (exact)", ha="center", fontsize=7.5, color=INK)
    ax.set_ylabel("between-region recurrence $R$", fontsize=9)
    _title(ax, "a. R vanishes without a region cycle")
    _style(ax)

    ax = axes[1]
    di = e["di"]
    ns = sorted({int(k.split("_")[1]) for k in di})
    x = np.arange(len(ns))
    ax.bar(x - 0.2, [di[f"eigen_{n}"]["te"] for n in ns], 0.4, color=PURPLE, label="slow eigen-macro")
    ax.bar(x + 0.2, [di[f"random_{n}"]["te"] for n in ns], 0.4, color=GRAY, label="random macro")
    for xi, n in zip(x, ns):
        ax.plot([xi - 0.4, xi + 0.4], [di[f"eigen_{n}"]["bias"]] * 2, color=INK, lw=1.0)
    ax.set_yscale("log")
    ax.set_xticks(x, [f"n = {n}" for n in ns], fontsize=8)
    ax.set_ylabel("transfer entropy micro $\\to$ macro (nats)", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    ax.text(x[-1] + 0.45, di[f"eigen_{ns[-1]}"]["bias"] * 1.3, "estimator bias", fontsize=7, ha="right")
    _title(ax, "b. the slow eigen-macro is autonomous")
    _style(ax)

    ax = axes[2]
    b = e["buffer"]
    ru = [row["rho_u"] for row in b]
    ax.plot(ru, [row["T_unconditional"] for row in b], "o-", color=AMBER, ms=4, label="$\\sum_\\tau I(Z_t;Z_{t+\\tau})$")
    ax.plot(ru, [row["T"] for row in b], "s-", color=GREEN, ms=4, label="$T = \\sum_\\tau I(Z_t;Z_{t+\\tau}\\mid u)$")
    ax.axhline(e["T_reference"], color=GRAY, ls="--", lw=0.9)
    ax.text(0.02, e["T_reference"] * 1.15, "reference network", fontsize=7.5, color=GRAY)
    ax.set_yscale("log")
    ax.set_xlabel("input autocorrelation $\\rho_u$", fontsize=9)
    ax.set_ylabel("nats per unit", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="center left")
    _title(ax, "c. a fast network that buffers a slow input")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_atlas(r, path):
    a, en = r["atlas"], r["ensemble"]
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 7.6))

    ax = axes[0, 0]
    fams = list(a["ratios"])
    x = np.arange(len(fams))
    floor = 2e-3
    for j, k in enumerate(NAMES):
        v = np.array([a["ratios"][f][k] for f in fams])
        ax.bar(x + (j - 1.5) * 0.19, np.maximum(v, floor), 0.19, color=COL[k], label=k)
        for xi, vi in zip(x, v):
            if vi == 0:
                ax.text(xi + (j - 1.5) * 0.19, floor * 1.3, "0", ha="center", fontsize=7)
    ax.axhline(FRAC, color=RED, lw=1.0, ls="--")
    ax.axhspan(a["frac_interval"][0], a["frac_interval"][1], color=RED, alpha=0.06, lw=0)
    ax.set_yscale("log")
    ax.set_ylim(floor / 1.5, 30)
    ax.set_xticks(x, [FAM_LABEL[f] for f in fams], fontsize=7.5)
    ax.set_ylabel("value / reference value", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, ncol=4, loc="upper left")
    _title(ax, "a. four families, each failing one invariant")
    _style(ax)

    ax = axes[0, 1]
    rs = np.array(en["spearman"])
    im = ax.imshow(rs, cmap="RdBu_r", vmin=-1, vmax=1)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{rs[i, j]:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if abs(rs[i, j]) > 0.6 else INK)
    ax.set_xticks(range(4), NAMES)
    ax.set_yticks(range(4), NAMES)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04).ax.tick_params(labelsize=7)
    _title(ax, f"b. rank correlations across {en['n']} random networks")

    ax = axes[1, 0]
    pats = list(en["patterns"].items())[:12]
    lab = [p if p != "RQTS" else "RQTS (all pass)" for p, _ in pats]
    cols = [GREEN if p == "RQTS" else (BLUE if p.count("-") == 1 else GRAY) for p, _ in pats]
    ax.barh(range(len(pats))[::-1], [c for _, c in pats], color=cols)
    ax.set_yticks(range(len(pats))[::-1], lab, fontsize=7.5, family="monospace")
    ax.set_xlabel("networks", fontsize=9)
    _title(ax, "c. pass patterns (dash marks a failed invariant)")
    _style(ax)

    ax = axes[1, 1]
    rows = en["rows"]
    th = en["thresholds"]
    P = np.array([[row[k] >= t for k, t in zip(NAMES, th)] for row in rows])
    conj = P.all(1)
    q = np.array([row["Q"] for row in rows])
    s = np.array([row["S"] for row in rows])
    ax.scatter(q[~conj], s[~conj], s=6, color=GRAY, alpha=0.5, label="fails at least one")
    ax.scatter(q[conj], s[conj], s=8, color=GREEN, alpha=0.8, label="passes all four")
    ax.axvline(th[1], color=AMBER, lw=0.9, ls="--")
    ax.axhline(th[3], color=PURPLE, lw=0.9, ls="--")
    ax.set_xlabel("perturbational repertoire $Q$", fontsize=9)
    ax.set_ylabel("stable macrostructure $S$", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="lower right")
    _title(ax, "d. Q and S across the ensemble")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_controllers(r, path):
    c = r["controllers"]
    titles = {"feedback": "a. feedback scale", "between": "b. between-region coupling",
              "global": "c. all-to-all coupling", "slow": "d. region-mean coupling",
              "iso": "e. equal-rate mixing", "gain": "f. spectral radius"}
    xl = {"feedback": "scale of feedback edges", "between": "between-region strength", "global": "all-to-all strength",
          "slow": "region-mean strength", "iso": "weight of the orthogonal operator",
          "gain": "spectral radius $\\rho(A)$"}
    fig, axes = plt.subplots(2, 3, figsize=(11.6, 6.6))
    for ax, key in zip(axes.flat, titles):
        d = c[key]
        for k in NAMES:
            ax.plot(d["grid"], np.maximum(d["series"][k], 1e-3), "o-", ms=3, color=COL[k], label=k)
        ax.axhline(FRAC, color=RED, lw=0.9, ls="--")
        ax.set_yscale("log")
        ax.set_ylim(1e-3 / 1.5, 40)
        ax.set_xlabel(xl[key], fontsize=9)
        cr = ", ".join(d["crossed"]) if d["crossed"] else "none"
        ax.text(0.97, 0.95, f"crosses threshold: {cr}", transform=ax.transAxes, ha="right", va="top", fontsize=7.5)
        _title(ax, titles[key])
        _style(ax)
    for ax in axes[:, 0]:
        ax.set_ylabel("value / reference value", fontsize=9)
    axes[0, 0].legend(fontsize=7.5, frameon=False, loc="lower right", ncol=4)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_statistics(r, path):
    st = r["statistics"]
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.4))

    ax = axes[0, 0]
    rr = st["margin_curve_r"]
    for k, c in zip(("1", "2", "3", "4"), (GRAY, BLUE, AMBER, RED)):
        ax.plot(rr, st["margin_curve"][k], color=c, lw=1.6, label=f"{k} invariant" + ("s" if k != "1" else ""))
    ax.set_xlabel("correlation of measurement errors", fontsize=9)
    ax.set_ylabel("margin for 90% joint sensitivity (SD)", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False)
    _title(ax, "a. margin each invariant needs")
    _style(ax)

    ax = axes[0, 1]
    ns = np.arange(20, 1201, 10)
    for f, c in (("0.0", GREEN), ("0.05", AMBER), ("0.1", RED)):
        p = st["label_noise"][f]
        ax.plot(ns, [cp_power(int(n), p) for n in ns], color=c, lw=1.2,
                label=f"label noise {float(f):.0%}: observed {p:.2f}")
    ax.axhline(0.8, color=GRAY, ls="--", lw=0.9)
    ax.set_xlabel("independent C+ epochs", fontsize=9)
    ax.set_ylabel("power: lower 95% bound above 0.80", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="lower right")
    _title(ax, "b. primary endpoint and label noise")
    _style(ax)

    ax = axes[1, 0]
    cs = list(st["ablation"])
    ax.bar(range(len(cs)), [st["ablation"][c] for c in cs], color=BLUE)
    for i, c in enumerate(cs):
        ax.text(i, st["ablation"][c] * 1.02 + 1, str(st["ablation"][c]), ha="center", fontsize=8)
    ax.set_xticks(range(len(cs)), [f"{float(c):.0%}" for c in cs])
    ax.set_xlabel("misclassified single-failure epochs", fontsize=9)
    ax.set_ylabel("paired epochs for 80% power", fontsize=9)
    _title(ax, "c. necessity of one invariant (McNemar)")
    _style(ax)

    ax = axes[1, 1]
    rng = np.random.default_rng(23)
    tk = rng.standard_normal((200000, 4))
    tc = rng.standard_normal(200000)
    leads = np.linspace(-1.5, 1.5, 31)
    ax.plot(leads, [np.mean((tk - L).min(1) < tc) for L in leads], color=RED, lw=1.6, label="loss: first failure before report change")
    ax.plot(leads, [np.mean((tk - L).max(1) < tc) for L in leads], color=BLUE, lw=1.6, label="recovery: last recovery before report change")
    ax.axhline(0.5, color=GRAY, ls=":", lw=0.9)
    ax.axvline(0, color=GRAY, lw=0.6)
    ax.plot([0, 0], [0.2, 0.8], "o", color=INK, ms=4)
    ax.text(0.08, 0.8, "4/5", fontsize=8, va="bottom")
    ax.text(0.08, 0.2, "1/5", fontsize=8, va="top")
    ax.set_xlabel("lead of the invariants over report (jitter SD)", fontsize=9)
    ax.set_ylabel("probability per transition", fontsize=9)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left")
    _title(ax, "d. order statistics of noisy transition times")
    _style(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def make_all(r, out: Path):
    plot_estimators(r, out / "estimators.png")
    plot_atlas(r, out / "atlas.png")
    plot_controllers(r, out / "controllers.png")
    plot_statistics(r, out / "statistics.png")
