"""Tests for analysis/reservoir_benchmarks.py — the NARMA-10 + memory-capacity
benchmark ported from NeuromorphicMyceliumChip's methodology (see module
docstring for full attribution)."""

import numpy as np
import pytest

from analysis.reservoir_benchmarks import (
    fit_ridge_readout,
    generate_narma10,
    memory_capacity,
    run_narma10_benchmark,
    tapped_delay_states,
)


def test_narma10_is_deterministic_given_seed():
    u1, y1 = generate_narma10(500, seed=42)
    u2, y2 = generate_narma10(500, seed=42)
    assert np.allclose(u1, u2)
    assert np.allclose(y1, y2)


def test_narma10_stays_finite():
    _, y = generate_narma10(2000, seed=7)
    assert np.all(np.isfinite(y))


def test_narma10_input_is_bounded():
    u, _ = generate_narma10(500, seed=1)
    assert u.min() >= 0.0
    assert u.max() <= 0.5


def test_ridge_readout_recovers_identity_substrate():
    """A substrate whose state trace literally IS the target should score
    near-zero NRMSE."""
    _, y = generate_narma10(1000, seed=42)
    states = tapped_delay_states(y, n_taps=3)
    result = fit_ridge_readout(states, y, washout=50)
    assert result.test_nrmse < 1e-3


def test_ridge_readout_fails_on_pure_noise():
    """A substrate with no relationship to the target should score close to
    the NRMSE of predicting the mean (i.e. ~1.0)."""
    _, y = generate_narma10(1000, seed=42)
    rng = np.random.default_rng(0)
    noise_states = tapped_delay_states(rng.normal(size=1000), n_taps=3)
    result = fit_ridge_readout(noise_states, y, washout=50)
    assert result.test_nrmse > 0.8


def test_memory_capacity_detects_known_lag():
    """A state that is a pure delayed copy of the input should show peak
    cross-correlation at exactly that lag."""
    rng = np.random.default_rng(3)
    inp = rng.uniform(size=2000)
    lag_true = 7
    state = np.zeros_like(inp)
    state[lag_true:] = inp[:-lag_true]

    result = memory_capacity(inp, state, max_lag=20)
    assert result.max_crosscorr_lag == lag_true
    assert result.has_temporal_memory


def test_memory_capacity_no_memory_on_independent_noise():
    rng = np.random.default_rng(4)
    inp = rng.normal(size=2000)
    state = rng.normal(size=2000)  # independent of inp
    result = memory_capacity(inp, state, max_lag=20)
    assert not result.has_temporal_memory


def test_run_narma10_benchmark_end_to_end_with_toy_reservoir():
    """A trivial 'reservoir' that just low-pass filters its input should run
    through the full benchmark pipeline without error and produce a
    well-formed result dict."""
    state = {"v": 0.0}

    def step_fn(u_t: float) -> None:
        state["v"] = 0.8 * state["v"] + 0.2 * u_t

    def read_fn() -> float:
        return state["v"]

    result = run_narma10_benchmark(step_fn, read_fn, n_steps=500, washout=50, seed=42)
    assert "train_nrmse" in result and "test_nrmse" in result
    assert result["n_train"] > 0 and result["n_test"] > 0
    assert np.isfinite(result["test_nrmse"])
