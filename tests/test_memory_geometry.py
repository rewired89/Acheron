"""Tests for analysis/memory_geometry.py — the write-axis / K_mem method
generalized from tasmorpho's methodology (see module docstring for full
attribution)."""

import numpy as np
import pytest

from analysis.memory_geometry import PerturbationTrial, compute_write_axis


def test_requires_at_least_two_trials():
    with pytest.raises(ValueError):
        compute_write_axis([PerturbationTrial(np.array([1.0]), 1.0, np.array([1.0]))])


def test_recovers_known_linear_write_map_1d_observable():
    rng = np.random.default_rng(1)
    A = np.array([[3.0, 0.2]])  # true 1D-observable <- 2D-perturbation write map
    trials = []
    for _ in range(200):
        p = rng.normal(size=2)
        shift = A @ p
        cost = 0.5 * abs(p[0]) + 4.0 * abs(p[1])
        trials.append(PerturbationTrial(p, cost, shift))

    result = compute_write_axis(trials)
    assert np.allclose(result.R, A, atol=0.3)
    # dim0 was cheaper per unit than dim1 in the ground truth
    assert np.diag(result.Q)[0] < np.diag(result.Q)[1]


def test_dominant_axis_aligns_with_more_efficient_observable_dimension():
    rng = np.random.default_rng(2)
    # Equal cost per unit; dim0 of perturbation writes strongly into
    # observable dim0, dim1 writes weakly into observable dim1.
    A = np.array([[5.0, 0.0], [0.0, 0.3]])
    trials = []
    for _ in range(300):
        p = rng.normal(size=2)
        shift = A @ p
        cost = abs(p[0]) + abs(p[1])
        trials.append(PerturbationTrial(p, cost, shift))

    result = compute_write_axis(trials)
    axis = np.abs(result.dominant_write_axis)
    assert axis[0] > axis[1]
    # top eigenvalue should dominate the second by a wide margin, matching
    # the 5.0 vs 0.3 asymmetry baked into A
    assert result.eigenvalues[0] > 10 * result.eigenvalues[1]


def test_k_mem_is_symmetric():
    rng = np.random.default_rng(3)
    A = rng.normal(size=(2, 3))
    trials = []
    for _ in range(100):
        p = rng.normal(size=3)
        shift = A @ p
        cost = np.abs(p).sum()
        trials.append(PerturbationTrial(p, cost, shift))

    result = compute_write_axis(trials)
    assert np.allclose(result.K_mem, result.K_mem.T)
