"""Estimators for the four invariants of the minimal conscious regime, a dissociation atlas, a random
ensemble, controller sweeps and the statistics of a conjunctive test.

Model class: a linear-Gaussian vector autoregression Z_{t+1} = A Z_t + B u_t + eta_t on N = 64 units
grouped into M = 8 regions of 8 units, eta ~ N(0, I).

    R  between-region recurrence: energy that returns to the perturbed region through other regions,
       divided by the energy that reaches other regions
    Q  perturbational repertoire: share of the response to a regional pulse that leaves the pulsed region,
       times the dissimilarity of the responses to different regions
    T  endogenous temporal depth: sum over lags of I(Z_t; Z_{t+tau}) given the input path, per unit
    S  stable macrostructure: test-retest overlap, across independent data windows, of the dynamically
       independent macro spanned by the slowest left eigenvectors of the fitted operator

R, Q and S are evaluated on the operator rescaled to spectral radius RHO_REF, so the spectral radius
enters through T alone.
"""
from __future__ import annotations

import numpy as np
from scipy import stats
from scipy.linalg import solve_discrete_lyapunov

N, M = 64, 8
NR = N // M
REG = np.repeat(np.arange(M), NR)
SAME = REG[:, None] == REG[None, :]
FEEDBACK = REG[:, None] < REG[None, :]       # edge j -> i with target region below source region
RHO_REF = 0.9
H = 60                                       # response horizon (0.9^60 < 2e-3)
FRAC = 0.5                                   # pass threshold as a fraction of the reference value
NAMES = ("R", "Q", "T", "S")


# ---------------------------------------------------------------------------------------------- estimators

def rho(A):
    return float(np.max(np.abs(np.linalg.eigvals(A))))


def normalize(A, r=RHO_REF):
    return A * (r / rho(A))


def powers(A, h=H):
    P = np.empty((h, N, N))
    X = np.eye(N)
    for t in range(h):
        X = A @ X
        P[t] = X
    return P


def R_measure(A):
    """Between-region return energy over out-of-region energy for unit impulses on every unit."""
    A = normalize(A)
    PA, PD = powers(A), powers(A * SAME)
    ret = np.sum(((PA - PD) * SAME[None]) ** 2)
    out = np.sum((PA * ~SAME[None]) ** 2)
    return float(ret / out) if out > 0 else 0.0


def responses(A):
    """Responses x_t = A^t x_0, t = 1..H, to a unit pulse spread over each region: shape (M, H, N)."""
    P = powers(normalize(A))
    X0 = SAME[:, ::NR].astype(float) / np.sqrt(NR)    # column r: unit vector on region r
    return np.einsum("tij,jr->rti", P, X0)


def Q_measure(A):
    Y = responses(A)
    integ = np.mean([np.sum(Y[r][:, REG != r] ** 2) / np.sum(Y[r] ** 2) for r in range(M)])
    cos = []
    for r in range(M):
        for s in range(r + 1, M):
            m = (REG != r) & (REG != s)
            a, b = Y[r][:, m].ravel(), Y[s][:, m].ravel()
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            cos.append(abs(a @ b) / (na * nb) if na > 1e-12 and nb > 1e-12 else 1.0)
    diff = 1.0 - float(np.mean(cos))
    return float(integ * diff), float(integ), diff


def lagged_mi(S0, C):
    """I(Z_t; Z_{t+tau}) for a stationary Gaussian process with covariance S0 and lag covariance C."""
    return 0.5 * (np.linalg.slogdet(S0)[1] - np.linalg.slogdet(S0 - C @ np.linalg.solve(S0, C.T))[1])


def T_measure(A, tol=1e-7, max_lag=20000):
    """Sum over lags of I(Z_t; Z_{t+tau} | input path), nats per unit. Given the input path the residual
    process is the autonomous one driven by eta, so the sum depends on A alone."""
    S0 = solve_discrete_lyapunov(A, np.eye(N))
    tot, Ak = 0.0, np.eye(N)
    for _ in range(max_lag):
        Ak = A @ Ak
        inc = lagged_mi(S0, Ak @ S0)
        tot += inc
        if inc < tol:
            break
    return float(tot / N)


def T_unconditional(A, Bmat, rho_u, tol=1e-7, max_lag=20000):
    """Same sum without conditioning, for Z driven by eta and by an AR(1) input u (unit innovations)."""
    k = Bmat.shape[1]
    J = np.block([[A, Bmat], [np.zeros((k, N)), rho_u * np.eye(k)]])
    SJ = solve_discrete_lyapunov(J, np.eye(N + k))
    S0 = SJ[:N, :N]
    tot, Jk = 0.0, np.eye(N + k)
    for _ in range(max_lag):
        Jk = J @ Jk
        inc = lagged_mi(S0, (Jk @ SJ)[:N, :N])
        tot += inc
        if inc < tol:
            break
    return float(tot / N)


def simulate(A, n, W, rng, burn=200):
    """n independent windows of length W of Z_{t+1} = A Z_t + eta_t: shape (n, W, N)."""
    Z = np.empty((W, N, n))
    x = np.zeros((N, n))
    eta = rng.standard_normal((W + burn, N, n))
    for t in range(W + burn):
        x = A @ x + eta[t]
        if t >= burn:
            Z[t - burn] = x
    return np.transpose(Z, (2, 0, 1))


def fit_var1(Z):
    return np.linalg.lstsq(Z[:-1], Z[1:], rcond=None)[0].T


def slow_bases(A, nmax):
    """Orthonormal bases of the left-invariant subspaces spanned by the n slowest modes, n = 1..nmax,
    with a split complex pair completed by its conjugate."""
    lam, W = np.linalg.eig(A.T)
    order = np.argsort(-np.abs(lam), kind="stable")
    lam, W = lam[order], W[:, order]
    out = []
    for n in range(1, nmax + 1):
        k = n
        if abs(lam[k - 1].imag) > 1e-12 and k < N and np.isclose(lam[k], np.conj(lam[k - 1])):
            k += 1
        V = np.concatenate([W[:, :k].real, W[:, :k].imag], axis=1)
        U, s, _ = np.linalg.svd(V, full_matrices=False)
        out.append(U[:, : int(np.sum(s > 1e-9 * s[0]))])
    return out


def S_measure(A, rng, n_windows=6, W=4000, nmax=12):
    Z = simulate(normalize(A), n_windows, W, rng)
    bases = [slow_bases(fit_var1(z), nmax) for z in Z]
    prof = []
    for n in range(nmax):
        ov, dims = [], []
        for i in range(n_windows):
            for j in range(i + 1, n_windows):
                Ui, Uj = bases[i][n], bases[j][n]
                d = max(Ui.shape[1], Uj.shape[1])
                ov.append(np.linalg.norm(Ui.T @ Uj) ** 2 / d)
                dims.append(d)
        c = np.mean(dims) / N
        prof.append(float((np.mean(ov) - c) / (1 - c)))
    k = int(np.argmax(prof))
    return prof[k], prof, k + 1


def invariants(A, rng):
    q = Q_measure(A)
    s, prof, n = S_measure(A, rng)
    return {"R": R_measure(A), "Q": q[0], "T": T_measure(A), "S": s,
            "Q_integration": q[1], "Q_differentiation": q[2], "S_dimension": n, "S_profile": prof,
            "rho": rho(A)}


# ------------------------------------------------------------------------------------------------ systems

def modular(seed, local=1.0, between=0.8, p=0.25, slow=1.4, glob=0.0, fb=1.0, iso=0.0, raw_rho=0.95):
    """Modular network: random within-region coupling, sparse random between-region coupling whose
    feedback edges are scaled by fb, one slow collective mode per region (region-mean coupling) and an
    optional all-to-all component of strength glob; a fraction iso of a random orthogonal operator
    (equal decay rates) is mixed in; rescaled to spectral radius raw_rho."""
    rng = np.random.default_rng(seed)
    Aloc = local * 0.5 * rng.standard_normal((N, N)) / np.sqrt(NR) * SAME
    Bw = rng.standard_normal((N, N)) * (rng.random((N, N)) < p) / np.sqrt(N * p)
    Ab = between * Bw * ~SAME * np.where(FEEDBACK, fb, 1.0)
    A = Aloc + Ab + slow * 0.5 * SAME / NR + glob * np.ones((N, N)) / N
    if iso > 0:
        Qo = np.linalg.qr(rng.standard_normal((N, N)))[0]
        A = (1 - iso) * A / rho(A) + iso * Qo
    return A * (raw_rho / rho(A))


def equal_rates(seed, raw_rho=0.95):
    """Scaled random orthogonal operator: every mode decays at the same rate."""
    Qo, Rr = np.linalg.qr(np.random.default_rng(seed).standard_normal((N, N)))
    return raw_rho * Qo * np.sign(np.diag(Rr))[None, :]


FAMILIES = {
    "reference": lambda s: modular(s),
    "no_R": lambda s: modular(s, between=1.6, fb=0.0),
    "no_Q": lambda s: modular(s, glob=8.0, raw_rho=0.995),
    "no_T": lambda s: modular(s, raw_rho=0.3),
    "no_S": lambda s: equal_rates(s + 1000),
}
TARGET = {"reference": None, "no_R": "R", "no_Q": "Q", "no_T": "T", "no_S": "S"}


def failures(vals, ref, frac=FRAC):
    return [k for k in NAMES if vals[k] < frac * ref[k]]


# --------------------------------------------------------------------------------- estimator properties

def estimator_checks():
    out = {}
    # R vanishes on region-acyclic systems and is positive on nonnegative systems with a region cycle
    acyc, cyc, nonneg_cyc = [], [], []
    for s in range(40):
        acyc.append(R_measure(modular(100 + s, fb=0.0)))
        cyc.append(R_measure(modular(100 + s, fb=0.3)))
        rng = np.random.default_rng(200 + s)
        A = np.abs(rng.standard_normal((N, N))) * (SAME | (rng.random((N, N)) < 0.05))
        nonneg_cyc.append(R_measure(A))
    out["R_acyclic_max"] = float(np.max(acyc))
    out["R_cyclic_min"] = float(np.min(cyc))
    out["R_nonneg_min"] = float(np.min(nonneg_cyc))
    out["R_acyclic"], out["R_cyclic"] = acyc, cyc

    # dynamical independence: the slow eigen-macro is autonomous, a random macro is not
    rng = np.random.default_rng(7)
    A = normalize(modular(1))
    Z = simulate(A, 1, 200000, rng)[0]
    res = {}
    for n in (1, 4, 8):
        L = slow_bases(A, n)[n - 1].T
        Lr = np.linalg.qr(rng.standard_normal((N, L.shape[0])))[0].T
        for tag, Lm in (("eigen", L), ("random", Lr)):
            Y = Z @ Lm.T
            resid = np.linalg.norm(Lm @ A - (Lm @ A @ np.linalg.pinv(Lm)) @ Lm) / np.linalg.norm(Lm @ A)
            # 2T x TE is asymptotically chi-square with N x dim degrees of freedom for an autonomous macro
            res[f"{tag}_{n}"] = {"dim": Lm.shape[0], "invariance_residual": float(resid),
                                 "te": float(transfer_entropy(Y, Z, p=5)), "bias": N * Lm.shape[0] / (2 * len(Z))}
    out["di"] = res
    out["di_eigen_te_over_bias_max"] = max(v["te"] / v["bias"] for k, v in res.items() if k.startswith("eigen"))
    out["di_random_te_over_bias_min"] = min(v["te"] / v["bias"] for k, v in res.items() if k.startswith("random"))
    out["di_eigen_resid_max"] = max(v["invariance_residual"] for k, v in res.items() if k.startswith("eigen"))

    # endogenous temporal depth: a fast network that buffers a slow input
    Af = modular(1, raw_rho=0.3)
    Bm = np.random.default_rng(9).standard_normal((N, 4)) / np.sqrt(4)
    rows = []
    for ru in (0.0, 0.5, 0.9, 0.97, 0.99):
        rows.append({"rho_u": ru, "T_unconditional": T_unconditional(Af, Bm, ru), "T": T_measure(Af)})
    out["buffer"] = rows
    out["T_reference"] = T_measure(modular(1))
    return out


def transfer_entropy(Y, Z, p=5):
    """Gaussian transfer entropy from the micro state Z_t to the macro Y_{t+1} given p lags of Y
    (half the log ratio of residual generalized variances; Barnett, Barrett and Seth 2009)."""
    T = len(Y)
    lagsY = np.hstack([Y[p - 1 - k: T - 1 - k] for k in range(p)])
    tgt = Y[p:]
    def resid_logdet(X):
        X = np.hstack([X, np.ones((len(X), 1))])
        beta = np.linalg.lstsq(X, tgt, rcond=None)[0]
        E = tgt - X @ beta
        return np.linalg.slogdet(np.atleast_2d(np.cov(E.T)))[1]
    return 0.5 * (resid_logdet(lagsY) - resid_logdet(np.hstack([lagsY, Z[p - 1: T - 1]])))


# ------------------------------------------------------------------------------------- dissociation atlas

def atlas(seeds=range(1, 21)):
    rng = np.random.default_rng(11)
    vals = {k: invariants(f(1), rng) for k, f in FAMILIES.items()}
    ref = vals["reference"]
    ratios = {k: {n: v[n] / ref[n] for n in NAMES} for k, v in vals.items()}
    # interval of threshold fractions for which every family fails exactly its target invariant
    lo, hi = 0.0, 1.0
    for k, t in TARGET.items():
        if t is None:
            continue
        lo = max(lo, ratios[k][t])
        hi = min(hi, min(ratios[k][n] for n in NAMES if n != t))
    robust = {}
    for k, f in FAMILIES.items():
        if TARGET[k] is None:
            continue
        ok = 0
        for s in seeds:
            r = invariants(FAMILIES["reference"](s), rng)
            v = invariants(f(s), rng)
            ok += failures(v, r) == [TARGET[k]]
        robust[k] = ok
    return {"values": vals, "ratios": ratios, "frac_interval": [lo, hi], "seed_success": robust,
            "n_seeds": len(list(seeds)),
            "exactly_one": {k: failures(vals[k], ref) for k in FAMILIES}}


# ----------------------------------------------------------------------------------------------- ensemble

def ensemble(n=1000, seed=3):
    rng = np.random.default_rng(seed)
    ref = invariants(FAMILIES["reference"](1), np.random.default_rng(11))
    rows = []
    for i in range(n):
        par = {"local": rng.uniform(0.3, 1.5), "between": rng.uniform(0.0, 1.6), "p": rng.uniform(0.05, 0.5),
               "slow": rng.uniform(0.0, 2.5), "glob": 0.0 if rng.random() < 0.5 else float(np.exp(rng.uniform(np.log(0.5), np.log(12)))),
               "fb": 0.0 if rng.random() < 0.2 else rng.uniform(0.0, 1.0),
               "iso": 0.0 if rng.random() < 0.5 else rng.uniform(0.0, 1.0), "raw_rho": rng.uniform(0.3, 0.99)}
        A = modular(10_000 + i, **par)
        v = invariants(A, rng)
        rows.append({**par, **{k: v[k] for k in NAMES}})
    X = np.array([[r[k] for k in NAMES] for r in rows])
    th = np.array([FRAC * ref[k] for k in NAMES])
    P = X >= th
    rs = stats.spearmanr(X).statistic
    pattern = {}
    for row in P:
        key = "".join(k if ok else "-" for k, ok in zip(NAMES, row))
        pattern[key] = pattern.get(key, 0) + 1
    conj = P.all(1)
    single = {k: int(np.sum((~P[:, i]) & P[:, [j for j in range(4) if j != i]].all(1))) for i, k in enumerate(NAMES)}
    false_pos = {k: float(np.mean(~conj[P[:, i]])) for i, k in enumerate(NAMES)}
    others = {k: P[:, [j for j in range(4) if j != i]].all(1) for i, k in enumerate(NAMES)}
    fail_given_others = {k: float(np.mean(~P[others[k], i])) for i, k in enumerate(NAMES)}
    n_others = {k: int(others[k].sum()) for k in NAMES}
    Rk = np.argsort(np.argsort(X, axis=0), axis=0).astype(float)
    Rk = (Rk - Rk.mean(0)) / Rk.std(0)
    r2 = {}
    for i, k in enumerate(NAMES):
        Xo = np.hstack([Rk[:, [j for j in range(4) if j != i]], np.ones((len(Rk), 1))])
        res = Rk[:, i] - Xo @ np.linalg.lstsq(Xo, Rk[:, i], rcond=None)[0]
        r2[k] = float(1 - res.var() / Rk[:, i].var())
    # variance carried by independent directions: eigenvalues of the rank-correlation matrix
    ev = np.sort(np.linalg.eigvalsh(rs))[::-1]
    return {"n": n, "spearman": rs.tolist(), "max_abs_offdiag": float(np.max(np.abs(rs - np.eye(4)))),
            "rank_corr_eigs": ev.tolist(), "patterns": dict(sorted(pattern.items(), key=lambda kv: -kv[1])),
            "n_conjunction": int(conj.sum()), "single_failures": single,
            "conj_fail_given_pass": false_pos, "fail_given_others_pass": fail_given_others,
            "n_others_pass": n_others, "rank_r2_from_others": r2, "max_rank_r2": max(r2.values()),
            "thresholds": th.tolist(), "rows": rows}


# ---------------------------------------------------------------------------------------- controller sweeps

SWEEPS = {
    "feedback": ("fb", np.linspace(0.0, 1.0, 11)),
    "between": ("between", np.linspace(0.0, 1.6, 11)),
    "global": ("glob", np.linspace(0.0, 12.0, 11)),
    "slow": ("slow", np.linspace(0.0, 2.5, 11)),
    "iso": ("iso", np.linspace(0.0, 1.0, 11)),
    "gain": ("raw_rho", np.linspace(0.3, 0.99, 11)),
}


def controllers():
    rng = np.random.default_rng(13)
    ref = invariants(FAMILIES["reference"](1), np.random.default_rng(11))
    out = {}
    for name, (par, grid) in SWEEPS.items():
        traj = [invariants(modular(1, **{par: float(x)}), rng) for x in grid]
        series = {k: [t[k] / ref[k] for t in traj] for k in NAMES}
        moved = [k for k in NAMES if max(series[k]) - min(series[k]) > 0.25]
        crossed = [k for k in NAMES if min(series[k]) < FRAC <= max(series[k])]
        out[name] = {"param": par, "grid": grid.tolist(), "series": series, "moved": moved, "crossed": crossed,
                     "range": {k: [min(series[k]), max(series[k])] for k in NAMES}}
    return out


# --------------------------------------------------------------------------------- conjunctive statistics

GH = np.polynomial.hermite_e.hermegauss(120)


def orthant(d, K, r):
    """P(Z_k > -d for all k) for K exchangeable standard normals with correlation r (Dunnett and Sobel 1955)."""
    if r <= 0:
        return float(stats.norm.cdf(d) ** K)
    if r >= 1:
        return float(stats.norm.cdf(d))
    z, w = GH
    return float(np.sum(w * stats.norm.cdf((d + np.sqrt(r) * z) / np.sqrt(1 - r)) ** K) / np.sqrt(2 * np.pi))


def margin(K, target, r):
    from scipy.optimize import brentq
    return float(brentq(lambda d: orthant(d, K, r) - target, -5, 10))


def cp_lower(x, n, alpha=0.05):
    return np.where(x > 0, stats.beta.ppf(alpha, np.maximum(x, 1), n - x + 1), 0.0)


def cp_power(n, p, bound=0.8, alpha=0.05):
    x = np.arange(n + 1)
    ok = cp_lower(x, n, alpha) > bound
    if not ok.any():
        return 0.0
    return float(stats.binom.sf(np.argmax(ok) - 1, n, p))


def n_required(p, bound=0.8, power=0.8, nmax=40000):
    """Smallest n with power >= target for every n' in [n, n + 50] (the exact power is sawtoothed)."""
    lo, hi = 10, nmax
    while lo < hi:                                 # coarse search on a smooth upper envelope
        mid = (lo + hi) // 2
        if cp_power(mid, p, bound) >= power:
            hi = mid
        else:
            lo = mid + 1
    n = max(10, lo - 400)
    while not all(cp_power(m, p, bound) >= power for m in range(n, n + 51)):
        n += 1
    return n


def mcnemar_power(n, pa, pb, alpha):
    """Exact conditional one-sided McNemar test on n independent pairs (outcome in arm A, outcome in arm B)."""
    p10, p01 = pa * (1 - pb), (1 - pa) * pb
    pd = p10 + p01
    if pd == 0:
        return 0.0
    th = p10 / pd
    nd = np.arange(n + 1)
    w = stats.binom.pmf(nd, n, pd)
    pw = 0.0
    for k, wk in zip(nd, w):
        if k == 0 or wk < 1e-14:
            continue
        x = np.arange(k + 1)
        crit = np.argmax(stats.binom.sf(x - 1, k, 0.5) <= alpha) if (stats.binom.sf(x - 1, k, 0.5) <= alpha).any() else k + 1
        pw += wk * stats.binom.sf(crit - 1, k, th)
    return float(pw)


def pairs_required(pa, pb, alpha, power=0.8, nmax=5000):
    lo, hi = 2, nmax
    while lo < hi:
        mid = (lo + hi) // 2
        if mcnemar_power(mid, pa, pb, alpha) >= power:
            hi = mid
        else:
            lo = mid + 1
    n = max(2, lo - 30)
    while not all(mcnemar_power(m, pa, pb, alpha) >= power for m in range(n, n + 11)):
        n += 1
    return n


def statistics():
    out = {}
    K, target = 4, 0.9
    out["margin_single"] = margin(1, target, 0.0)
    out["margin_indep"] = margin(K, target, 0.0)
    out["margin_corr"] = {str(r): margin(K, target, r) for r in (0.0, 0.25, 0.5, 0.75, 0.9)}
    out["margin_curve"] = {str(k): [margin(k, target, r) for r in np.linspace(0, 0.95, 20)] for k in (1, 2, 3, 4)}
    out["margin_curve_r"] = np.linspace(0, 0.95, 20).tolist()
    rng = np.random.default_rng(17)
    d, r = out["margin_corr"]["0.5"], 0.5
    Zc = np.sqrt(r) * rng.standard_normal((400000, 1)) + np.sqrt(1 - r) * rng.standard_normal((400000, K))
    out["mc_orthant_r05"] = float(np.mean((Zc > -d).all(1)))

    # anchor: four tests at the sensitivity PCI* reached in minimally conscious patients (36 of 38)
    s = 36 / 38
    out["pci_mcs_sens"] = s
    out["pci_mcs_ci"] = [float(stats.beta.ppf(0.025, 36, 3)), float(stats.beta.ppf(0.975, 37, 2))]
    out["conj_indep"] = s ** 4
    out["conj_r05"] = orthant(float(stats.norm.ppf(s)), 4, 0.5)

    # label noise: observed sensitivity when a fraction f of C+ labels belongs to unconscious epochs
    se, sp = 0.9, 0.9
    out["label_noise"] = {str(f): (1 - f) * se + f * (1 - sp) for f in (0.0, 0.05, 0.1, 0.2)}
    # sample size for the primary endpoint: one-sided 95% Clopper-Pearson lower bound above 0.80
    out["n_eff"] = {str(f): n_required(round((1 - f) * se + f * (1 - sp), 6)) for f in (0.0, 0.01, 0.02, 0.03, 0.04, 0.05)}
    out["n_eff_f10"] = n_required(round(0.9 * se + 0.1 * (1 - sp), 6))
    out["n_eff_ratio_f05"] = out["n_eff"]["0.05"] / out["n_eff"]["0.0"]
    # clustering of epochs within participants
    m_ep, icc = 10, 0.1
    de = 1 + (m_ep - 1) * icc
    out["design_effect"] = de
    out["participants"] = {f: int(np.ceil(n * de / m_ep)) for f, n in out["n_eff"].items()}
    out["max_f_for_40"] = max(float(f) for f, n in out["participants"].items() if n <= 40)
    out["epochs_per_participant"], out["icc"] = m_ep, icc

    # necessity (ablation) and model comparison: paired C+ rates, all-pass epoch vs only-i-fails epoch
    p1, f0, alpha = 0.9, 0.05, 0.05 / 4
    out["ablation"] = {str(c): pairs_required(p1, c * p1 + (1 - c) * f0, alpha) for c in (0.0, 0.25, 0.5, 0.75)}

    # transition order: the conjunction is lost at its first failure and regained at its last recovery
    rng = np.random.default_rng(19)
    n_mc = 400000
    tk = rng.standard_normal((n_mc, K))
    tc = rng.standard_normal(n_mc)
    out["order_null_loss"] = float(np.mean(tk.min(1) < tc))
    out["order_null_recovery"] = float(np.mean(tk.max(1) < tc))
    out["order_exact_loss"] = K / (K + 1)
    out["order_exact_recovery"] = 1 / (K + 1)
    out["order_null_loss_sigC2"] = float(np.mean(tk.min(1) < 2 * tc))
    out["emax4"] = float(np.mean(tk.max(1)))
    n_tr = 120
    crit_naive = int(stats.binom.isf(0.05, n_tr, 0.5)) + 1
    out["naive_false_positive"] = float(stats.binom.sf(crit_naive - 1, n_tr, K / (K + 1)))
    crit = int(stats.binom.isf(0.05, n_tr, K / (K + 1))) + 1
    out["order_power"] = {}
    for lead in (0.25, 0.5, 1.0):
        q = float(np.mean((tk - lead).min(1) < tc))
        out["order_power"][str(lead)] = {"q": q, "power": float(stats.binom.sf(crit - 1, n_tr, q))}
    out["n_transitions"] = n_tr
    return out


# --------------------------------------------------------------------------------------------------- run

def run():
    est = estimator_checks()
    atl = atlas()
    ens = ensemble()
    ctl = controllers()
    st = statistics()
    ref = atl["values"]["reference"]
    checks = {
        "R_zero_on_acyclic": est["R_acyclic_max"] < 1e-12,
        "R_positive_with_cycle": est["R_cyclic_min"] > 1e-3 and est["R_nonneg_min"] > 1e-3,
        "eigen_macro_invariant": est["di_eigen_resid_max"] < 1e-10,
        "eigen_macro_te_at_bias": est["di_eigen_te_over_bias_max"] < 1.5,
        "random_macro_te_large": est["di_random_te_over_bias_min"] > 100,
        "buffer_conditioning": est["buffer"][-1]["T_unconditional"] > 10 * est["buffer"][-1]["T"],
        "buffer_T_independent_of_input": len({round(r["T"], 12) for r in est["buffer"]}) == 1,
        "atlas_exactly_one": all(atl["exactly_one"][k] == ([TARGET[k]] if TARGET[k] else []) for k in FAMILIES),
        "atlas_interval_nonempty": atl["frac_interval"][0] < FRAC < atl["frac_interval"][1],
        "atlas_seed_robust": all(v >= 0.8 * atl["n_seeds"] for v in atl["seed_success"].values()),
        "gain_only_moves_T": ctl["gain"]["moved"] == ["T"] and ctl["gain"]["crossed"] == ["T"],
        "feedback_crosses_only_R": ctl["feedback"]["crossed"] == ["R"],
        "RQS_gain_invariant": all(max(ctl["gain"]["series"][k]) - min(ctl["gain"]["series"][k]) < 1e-6 for k in ("R", "Q")),
        "ensemble_all_singles_present": all(v > 0 for v in ens["single_failures"].values()),
        "orthant_mc_matches": abs(st["mc_orthant_r05"] - 0.9) < 0.002,
        "margin_monotone_in_r": all(np.diff(list(st["margin_corr"].values())) < 0),
        "margin_limits": abs(st["margin_corr"]["0.0"] - st["margin_indep"]) < 1e-9 and st["margin_corr"]["0.9"] > st["margin_single"],
        "order_null_matches_exact": abs(st["order_null_loss"] - 0.8) < 0.003 and abs(st["order_null_recovery"] - 0.2) < 0.003,
        "conj_indep_value": abs(st["conj_indep"] - (36 / 38) ** 4) < 1e-12,
        "reference_positive": all(ref[k] > 0 for k in NAMES),
    }
    return {"params": {"N": N, "M": M, "rho_ref": RHO_REF, "horizon": H, "threshold_fraction": FRAC},
            "estimators": est, "atlas": atl, "ensemble": ens, "controllers": ctl, "statistics": st,
            "checks": checks}
