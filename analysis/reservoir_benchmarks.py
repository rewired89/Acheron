"""Substrate-agnostic reservoir-computing benchmarks: NARMA-10 + memory capacity.

METHODOLOGY SOURCE (not vendored code — independently implemented from the
published methodology, generalized to any substrate):

  Ozgur Telhan et al., "Morphologically Tunable Mycelium Chips for Physical
  Reservoir Computing," bioRxiv 2025.08.20.671348 (also Scientific Reports,
  2026, DOI 10.1038/s41598-026-55550-5). Code: github.com/otelhan/
  NeuromorphicMyceliumChip (MIT license). That repository trains a
  PEDOT:PSS-infused mycelium network as a physical reservoir on the NARMA-10
  benchmark and characterizes its temporal memory via autocorrelation /
  cross-correlation analysis. Their implementation (mycelium_narma10.py,
  mycelium_memory_test.py) is a PyQt5 desktop app tightly coupled to
  Digilent hardware I/O, so it isn't reusable as a library. This module
  reimplements the substrate-agnostic parts of their method — the standard
  NARMA-10 sequence, a ridge-regression readout, and correlation-based
  memory-capacity analysis — so ANY Acheron substrate simulation can be
  scored on the same benchmark used to validate a real physical bio-reservoir.

NARMA-10 itself is a standard nonlinear-autoregressive benchmark from the
reservoir-computing literature (Atiya & Parlos, 2000), not proprietary to
either project.

WHAT THIS DOES NOT DO:
This scores a *simulation* of an Acheron-designed circuit, not a wet-lab
measurement. A high or low NRMSE here says "this designed circuit, as
currently modeled, does/doesn't behave like a nonlinear memory reservoir
in silico" — it is not evidence about real biological tissue until someone
runs the equivalent experiment on the actual substrate. Numbers below are
computed directly from the caller-supplied simulation; nothing is invented.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Callable, Optional


# ======================================================================
# NARMA-10 sequence generation (standard benchmark, Atiya & Parlos 2000;
# formula matches the variant used in NeuromorphicMyceliumChip's
# mycelium_narma10.py:generate_narma10_data)
# ======================================================================
def generate_narma10(n_steps: int, order: int = 10, seed: Optional[int] = None) -> tuple[np.ndarray, np.ndarray]:
    """Generate a NARMA-`order` input/target sequence.

    Returns (u, y): u is i.i.d. Uniform(0, 0.5) input, y is the nonlinear
    autoregressive target:

        y[t] = 0.3*y[t-1] + 0.05*y[t-1]*sum(y[t-1-i] for i in range(order))
               + 1.5*u[t-1]*u[t-order] + 0.1
    """
    rng = np.random.default_rng(seed)
    u = rng.uniform(0, 0.5, n_steps)
    y = np.zeros(n_steps)
    for t in range(order, n_steps):
        window_sum = y[t - order : t].sum()
        y[t] = (
            0.3 * y[t - 1]
            + 0.05 * y[t - 1] * window_sum
            + 1.5 * u[t - 1] * u[t - order]
            + 0.1
        )
    return u, y


# ======================================================================
# Ridge-regression readout (the standard reservoir-computing readout —
# matches the "ridge regression readout with nonlinear feature expansion"
# NeuromorphicMyceliumChip's README describes using on their NARMA-10 data)
# ======================================================================
@dataclass
class ReadoutResult:
    train_nrmse: float
    test_nrmse: float
    weights: np.ndarray
    n_train: int
    n_test: int


def _nrmse(pred: np.ndarray, target: np.ndarray) -> float:
    rmse = np.sqrt(np.mean((pred - target) ** 2))
    spread = target.std()
    return float(rmse / spread) if spread > 0 else float("nan")


def fit_ridge_readout(
    states: np.ndarray,
    target: np.ndarray,
    washout: int = 100,
    train_frac: float = 0.7,
    ridge_alpha: float = 1e-4,
) -> ReadoutResult:
    """Fit a ridge-regression readout from reservoir states to a target series.

    `states` is (n_steps, n_features) — e.g. a single voltage trace reshaped
    to (n_steps, 1), or a tapped-delay-line expansion for richer readout.
    Washout removes the initial transient before the reservoir has "seen"
    enough input to reflect it in its state.
    """
    assert states.shape[0] == target.shape[0], "states and target must align in time"
    n = states.shape[0]
    usable = np.arange(washout, n)
    split = washout + int((n - washout) * train_frac)

    X = np.hstack([states, np.ones((n, 1))])  # bias term
    train_idx = np.arange(washout, split)
    test_idx = np.arange(split, n)

    X_train, y_train = X[train_idx], target[train_idx]
    X_test, y_test = X[test_idx], target[test_idx]

    # Closed-form ridge: w = (X^T X + alpha I)^-1 X^T y
    reg = ridge_alpha * np.eye(X_train.shape[1])
    reg[-1, -1] = 0.0  # don't regularize the bias term
    w = np.linalg.solve(X_train.T @ X_train + reg, X_train.T @ y_train)

    train_pred = X_train @ w
    test_pred = X_test @ w

    return ReadoutResult(
        train_nrmse=_nrmse(train_pred, y_train),
        test_nrmse=_nrmse(test_pred, y_test),
        weights=w,
        n_train=len(train_idx),
        n_test=len(test_idx),
    )


def tapped_delay_states(x: np.ndarray, n_taps: int = 5) -> np.ndarray:
    """Expand a 1D state trace into a tapped-delay-line feature matrix,
    giving the ridge readout access to recent history (a cheap stand-in for
    a richer reservoir readout, same idea as NeuromorphicMyceliumChip's
    multi-channel voltage readout)."""
    n = len(x)
    feats = np.zeros((n, n_taps))
    for i in range(n_taps):
        feats[i:, i] = x[: n - i] if i > 0 else x
        if i > 0:
            feats[:i, i] = x[0]  # pad the start with the initial value
    return feats


# ======================================================================
# NARMA-10 benchmark driver — plugs any Acheron simulation in as the
# "reservoir" via a (step_fn, read_fn) pair
# ======================================================================
def run_narma10_benchmark(
    step_fn: Callable[[float], None],
    read_fn: Callable[[], float],
    n_steps: int = 2000,
    order: int = 10,
    washout: int = 100,
    n_taps: int = 5,
    seed: Optional[int] = None,
) -> dict:
    """Drive a substrate through the NARMA-10 input and score a ridge
    readout on predicting the NARMA-10 target from the substrate's state
    trajectory.

    step_fn(u_t): advances the substrate one step, using u_t as forcing input
    read_fn(): returns the substrate's current scalar state (e.g. voltage)
    """
    u, y = generate_narma10(n_steps, order=order, seed=seed)

    trace = np.zeros(n_steps)
    for t in range(n_steps):
        step_fn(u[t])
        trace[t] = read_fn()

    states = tapped_delay_states(trace, n_taps=n_taps)
    result = fit_ridge_readout(states, y, washout=washout)

    return {
        "input": u,
        "target": y,
        "state_trace": trace,
        "train_nrmse": result.train_nrmse,
        "test_nrmse": result.test_nrmse,
        "n_train": result.n_train,
        "n_test": result.n_test,
    }


# ======================================================================
# Memory-capacity analysis — autocorrelation / cross-correlation, matching
# NeuromorphicMyceliumChip's mycelium_memory_test.py methodology
# ======================================================================
@dataclass
class MemoryCapacityResult:
    lags: np.ndarray
    autocorrelation: np.ndarray
    cross_correlation: np.ndarray
    max_autocorr_lag: int
    max_crosscorr_lag: int
    has_temporal_memory: bool  # heuristic threshold, same 0.2 / 0.1 cutoffs
    #  NeuromorphicMyceliumChip's README reports using for "temporal memory
    # effects" detection


def memory_capacity(
    input_series: np.ndarray, state_series: np.ndarray, max_lag: int = 50
) -> MemoryCapacityResult:
    """Characterize a substrate's temporal memory via lagged correlations.

    Autocorrelation of the state trace reveals how long its own past
    influences its present; cross-correlation between past input and
    present state reveals how long an input's effect persists — the
    operational definition of "memory" a reservoir-computing substrate
    needs to be useful.
    """
    state = np.asarray(state_series, dtype=float)
    inp = np.asarray(input_series, dtype=float)
    state_c = state - state.mean()
    inp_c = inp - inp.mean()

    lags = np.arange(1, max_lag + 1)
    autocorr = np.array([
        np.corrcoef(state_c[:-lag], state_c[lag:])[0, 1] if lag < len(state_c) else 0.0
        for lag in lags
    ])
    crosscorr = np.array([
        np.corrcoef(inp_c[:-lag], state_c[lag:])[0, 1] if lag < len(inp_c) else 0.0
        for lag in lags
    ])
    autocorr = np.nan_to_num(autocorr)
    crosscorr = np.nan_to_num(crosscorr)

    max_auto_idx = int(np.argmax(np.abs(autocorr)))
    max_cross_idx = int(np.argmax(np.abs(crosscorr)))

    has_memory = bool(np.max(np.abs(autocorr)) > 0.2 or np.max(np.abs(crosscorr)) > 0.1)

    return MemoryCapacityResult(
        lags=lags,
        autocorrelation=autocorr,
        cross_correlation=crosscorr,
        max_autocorr_lag=int(lags[max_auto_idx]),
        max_crosscorr_lag=int(lags[max_cross_idx]),
        has_temporal_memory=has_memory,
    )
