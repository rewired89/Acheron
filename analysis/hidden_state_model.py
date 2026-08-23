"""Latent-threshold model of planarian hidden regenerative (bioelectric)
memory: does a transient bioelectric perturbation leave a persistent,
graded "written" state that a later re-cut can reveal?

METHODOLOGY AND DATA SOURCE (not vendored code — independently
reimplemented from the published methodology and the same reconstructed
published counts):

  Marcel Blattner, "Hidden regenerative state in planarians: A geometric
  model of bioelectric memory using Tangential Action Spaces," bioRxiv
  2026, DOI 10.64898/2026.04.01.715890. Code: github.com/marcelbtec/
  tasmorpho (MIT license), script 03_reduced_count_fit.py.

THE BIOLOGICAL QUESTION:
Amputated planarian fragments normally regenerate a head at the anterior
end and a tail at the posterior end. Transient perturbation of the
bioelectric state (gap-junction blockade via 8-hydroxy-2-deoxyguanosine
[8-OH], or altered Na+/K+ permeability via nigericin/monensin) can cause a
fragment to regenerate a head at BOTH ends instead — a stable
double-headed (DH) phenotype. The perturbation is transient; the outcome
is permanent. A "challenge" re-cut of worms that look single-headed (SH)
reveals that some fraction still carry a hidden, graded memory of the
original perturbation.

MODEL (probit latent-threshold, unit variance, immediate threshold fixed
at 0 — see tasmorpho's README for the full derivation):
  - mu_drug: latent write mean induced by each drug
  - p_immediate = Phi(mu_drug)             -- probability of DH right after treatment
  - theta_ch:   challenge threshold revealed by a second amputation
  - p_challenge_given_SH = [Phi(-mu) - Phi(theta_ch - mu)] / Phi(-mu)

Only 4 free parameters (mu_8OH, mu_nigericin, mu_monensin, theta_ch), fit
to published phenotype counts. The 8-OH immediate + challenge counts are
the primary fit targets; nigericin/monensin immediate counts set their
latent positions; and — the actual test of the model — nigericin/monensin
CHALLENGE penetrance is a held-out prediction never used in fitting.

WHAT THIS DOES NOT DO:
The counts below are Blattner's (2026) reconstruction of published
experimental phenotype counts, reused here as-is (public, citable,
already-measured data) rather than re-derived from the original wet-lab
papers directly — per Acheron's no-numeric-invention rule, anyone using
these numbers for a real decision should trace them back through
tasmorpho to their primary sources before treating them as final.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist
from typing import Callable, Optional

import numpy as np

try:
    from scipy.optimize import minimize as _scipy_minimize
except ImportError:  # pragma: no cover - scipy is in requirements.txt but keep this optional
    _scipy_minimize = None

_ND = NormalDist()


@dataclass(frozen=True)
class CountDatum:
    label: str
    successes: int
    trials: int
    role: str
    description: str


# Reconstructed phenotype counts, as published in Blattner (2026) / tasmorpho.
COUNTS: tuple[CountDatum, ...] = (
    CountDatum("8OH_immediate_DH", 143, 573, "primary_fit_target",
               "Immediate double-headed outcomes after 8-OH"),
    CountDatum("8OH_challenge_DH_among_immediate_SH", 36, 155, "primary_fit_target",
               "Challenge double-headed outcomes after water re-cut of 8-OH immediate SH worms"),
    CountDatum("nigericin_immediate_DH", 17, 132, "condition_setting",
               "Immediate double-headed outcomes after nigericin"),
    CountDatum("monensin_immediate_DH", 11, 89, "condition_setting",
               "Immediate double-headed outcomes after monensin"),
)

PARAM_NAMES = ("mu_8OH", "mu_nigericin", "mu_monensin", "theta_ch")


def phi_cdf(x: float) -> float:
    return _ND.cdf(float(x))


def phi_inv(p: float) -> float:
    eps = 1e-12
    p = min(max(float(p), eps), 1.0 - eps)
    return _ND.inv_cdf(p)


def _clip_prob(p: float) -> float:
    return min(max(float(p), 1e-12), 1.0 - 1e-12)


def p_immediate(mu: float) -> float:
    """P(double-headed immediately after treatment)."""
    return phi_cdf(mu)


def p_challenge_given_sh(mu: float, theta_ch: float) -> float:
    """P(double-headed on challenge re-cut | appeared single-headed immediately)."""
    denom = phi_cdf(-mu)
    if denom <= 0.0:
        return 1.0
    return _clip_prob((phi_cdf(-mu) - phi_cdf(theta_ch - mu)) / denom)


def negative_log_likelihood(params: np.ndarray) -> float:
    mu_8oh, mu_nig, mu_mon, theta_ch = (float(p) for p in params)
    probs = {
        "8OH_immediate_DH": p_immediate(mu_8oh),
        "nigericin_immediate_DH": p_immediate(mu_nig),
        "monensin_immediate_DH": p_immediate(mu_mon),
        "8OH_challenge_DH_among_immediate_SH": p_challenge_given_sh(mu_8oh, theta_ch),
    }
    total = 0.0
    for datum in COUNTS:
        p = _clip_prob(probs[datum.label])
        y, n = datum.successes, datum.trials
        total -= y * math.log(p) + (n - y) * math.log(1.0 - p)
    return total


def closed_form_estimate() -> np.ndarray:
    """Closed-form MLE for (mu_8OH, mu_nigericin, mu_monensin, theta_ch)."""
    by_label = {d.label: d for d in COUNTS}

    mu_8oh = phi_inv(by_label["8OH_immediate_DH"].successes / by_label["8OH_immediate_DH"].trials)
    mu_nig = phi_inv(by_label["nigericin_immediate_DH"].successes / by_label["nigericin_immediate_DH"].trials)
    mu_mon = phi_inv(by_label["monensin_immediate_DH"].successes / by_label["monensin_immediate_DH"].trials)

    chal = by_label["8OH_challenge_DH_among_immediate_SH"]
    q_8oh = chal.successes / chal.trials
    theta_ch = mu_8oh + phi_inv(phi_cdf(-mu_8oh) * (1.0 - q_8oh))
    return np.array([mu_8oh, mu_nig, mu_mon, theta_ch])


def _finite_diff_gradient(func: Callable[[np.ndarray], float], x: np.ndarray, step: float = 1e-6) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    steps = np.maximum(step, step * np.maximum(1.0, np.abs(x)))
    g = np.zeros(x.size)
    for i in range(x.size):
        e = np.zeros(x.size)
        e[i] = steps[i]
        g[i] = (func(x + e) - func(x - e)) / (2 * steps[i])
    return g


def _finite_diff_hessian(func: Callable[[np.ndarray], float], x: np.ndarray, step: float = 1e-5) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    n = x.size
    steps = np.maximum(step, step * np.maximum(1.0, np.abs(x)))
    H = np.zeros((n, n))
    fx = func(x)
    for i in range(n):
        ei = np.zeros(n); ei[i] = steps[i]
        H[i, i] = (func(x + ei) - 2 * fx + func(x - ei)) / (steps[i] ** 2)
        for j in range(i + 1, n):
            ej = np.zeros(n); ej[j] = steps[j]
            H[i, j] = H[j, i] = (
                func(x + ei + ej) - func(x + ei - ej) - func(x - ei + ej) + func(x - ei - ej)
            ) / (4 * steps[i] * steps[j])
    return H


def delta_method_interval(
    scalar_func: Callable[[np.ndarray], float], xhat: np.ndarray, cov: np.ndarray, z: float = 1.96
) -> tuple[float, float, float, float]:
    """Point estimate, SE, and (lo, hi) 95% CI for a scalar function of the fitted params."""
    estimate = float(scalar_func(xhat))
    grad = _finite_diff_gradient(scalar_func, xhat)
    variance = max(float(grad @ cov @ grad), 0.0)
    se = math.sqrt(variance)
    return estimate, se, max(0.0, estimate - z * se), min(1.0, estimate + z * se)


@dataclass
class FitResult:
    params: np.ndarray  # (mu_8OH, mu_nigericin, mu_monensin, theta_ch)
    cov: np.ndarray
    nelder_mead_agrees: Optional[bool]
    held_out_nigericin_challenge: tuple[float, float, float, float]  # estimate, se, lo, hi
    held_out_monensin_challenge: tuple[float, float, float, float]


def fit(cross_check_with_scipy: bool = True) -> FitResult:
    """Fit the model and compute held-out challenge-penetrance predictions
    for nigericin and monensin — the actual test of the model, since those
    counts are never used in fitting."""
    xhat = closed_form_estimate()

    nm_agrees = None
    if cross_check_with_scipy and _scipy_minimize is not None:
        res = _scipy_minimize(negative_log_likelihood, x0=xhat, method="Nelder-Mead",
                               options={"xatol": 1e-12, "fatol": 1e-12, "maxiter": 20000})
        nm_agrees = bool(np.allclose(res.x, xhat, atol=1e-3)) if res.success else False

    hessian = _finite_diff_hessian(negative_log_likelihood, xhat)
    cov = np.linalg.inv(hessian)

    nig_pred = delta_method_interval(lambda p: p_challenge_given_sh(p[1], p[3]), xhat, cov)
    mon_pred = delta_method_interval(lambda p: p_challenge_given_sh(p[2], p[3]), xhat, cov)

    return FitResult(
        params=xhat,
        cov=cov,
        nelder_mead_agrees=nm_agrees,
        held_out_nigericin_challenge=nig_pred,
        held_out_monensin_challenge=mon_pred,
    )
