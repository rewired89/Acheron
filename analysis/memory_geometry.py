"""Write-axis geometry: which perturbation direction most efficiently writes
into a substrate's persistent memory state, for the least energy?

METHODOLOGY SOURCE (not vendored code — independently implemented from the
published methodology, generalized to any substrate):

  Marcel Blattner, "Hidden regenerative state in planarians: A geometric
  model of bioelectric memory using Tangential Action Spaces," bioRxiv
  2026, DOI 10.64898/2026.04.01.715890. Code: github.com/marcelbtec/
  tasmorpho (MIT license).

tasmorpho's script 01 (01_betse_local_grounding.py) computes, from BETSE
bioelectric-tissue-simulator perturbation trials:

  Q        — quadratic cost matrix: energetic cost (excess ion flux) of a
             perturbation
  R        — write map: how a perturbation direction shifts macroscopic
             observables (mean Vmem, gap-junction contrast)
  K_mem    — memory co-metric = R Q^-1 R^T, the induced metric on the
             observable endpoint space

The eigenvectors of K_mem rank perturbation directions by how cheaply they
convert energy into a shift of the persistent/regenerative state; the top
eigenvector is the *dominant write axis*, directions near-orthogonal to it
are energetically wasted ("silent" perturbations).

This module reimplements that linear algebra in a substrate-agnostic form:
instead of requiring BETSE, it takes a list of (perturbation_vector,
energy_cost, observable_shift) trials from ANY simulation or experiment —
so it can be pointed at Acheron's own designed circuits (e.g.
GardnerToggleCell), not just BETSE tissue models.

WHAT THIS DOES NOT DO:
K_mem here is fit from whatever trial data is handed to it — usually a
simulation sweep. It identifies the efficient write axis *of that model*,
not a wet-lab-validated claim about real tissue, exactly as tasmorpho's own
README is explicit that the BETSE grounding is a model, calibrated against
published phenotype counts, not a first-principles derivation from raw
physics.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass


@dataclass
class PerturbationTrial:
    """One perturbation applied to a substrate, and what it cost/produced.

    perturbation: the perturbation parameter vector (e.g. [delta_alpha1,
        delta_alpha2, delta_strength_ratio] for GardnerToggleCell, or
        [na_permeability_delta, k_permeability_delta, gj_block_frac] for a
        BETSE-style tissue model).
    energy_cost: a scalar cost for applying this perturbation (e.g.
        integrated excess ion flux, or any other measured/simulated
        energetic proxy).
    observable_shift: the resulting shift in the substrate's macroscopic,
        persistent observable(s) (e.g. [delta_mean_V_after_settling]).
    """

    perturbation: np.ndarray
    energy_cost: float
    observable_shift: np.ndarray


@dataclass
class WriteAxisResult:
    Q: np.ndarray
    R: np.ndarray
    K_mem: np.ndarray
    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    dominant_write_axis: np.ndarray
    dominant_eigenvalue: float
    n_trials: int


def compute_write_axis(trials: list[PerturbationTrial], ridge: float = 1e-8) -> WriteAxisResult:
    """Fit Q, R, and K_mem = R Q^-1 R^T from a set of perturbation trials,
    and return the dominant write axis (top eigenvector of K_mem).

    Q is estimated as a diagonal cost matrix from the mean energy cost per
    perturbation-space dimension (a simplification of tasmorpho's
    trial-covariance-based Q — appropriate when trials vary one or a few
    perturbation dimensions at a time, as in a parameter sweep). R is
    estimated by least-squares regression of observable_shift onto
    perturbation across all trials — the linearized local write map.
    """
    if len(trials) < 2:
        raise ValueError("compute_write_axis needs at least 2 trials to fit R")

    P = np.array([t.perturbation for t in trials], dtype=float)  # (n, d_p)
    S = np.array([t.observable_shift for t in trials], dtype=float)  # (n, d_o)
    costs = np.array([t.energy_cost for t in trials], dtype=float)  # (n,)

    n, d_p = P.shape
    d_o = S.shape[1]

    # R: least-squares fit of S = P @ R^T  ->  R^T = pinv(P) @ S
    R_T, *_ = np.linalg.lstsq(P, S, rcond=None)
    R = R_T.T  # (d_o, d_p)

    # Q: diagonal cost per perturbation-space dimension, estimated as the
    # energy cost weighted by how much each trial moved along each
    # dimension (normalized so a trial that barely perturbed dimension i
    # doesn't inflate its apparent cost).
    weights = np.abs(P) / (np.abs(P).sum(axis=1, keepdims=True) + 1e-12)
    per_dim_cost = (weights * costs[:, None]).sum(axis=0) / (weights.sum(axis=0) + 1e-12)
    Q = np.diag(np.maximum(per_dim_cost, ridge))

    K_mem = R @ np.linalg.inv(Q) @ R.T  # (d_o, d_o)
    # Symmetrize to kill float asymmetry before eigendecomposition
    K_mem = (K_mem + K_mem.T) / 2.0

    eigvals, eigvecs = np.linalg.eigh(K_mem)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    return WriteAxisResult(
        Q=Q,
        R=R,
        K_mem=K_mem,
        eigenvalues=eigvals,
        eigenvectors=eigvecs,
        dominant_write_axis=eigvecs[:, 0],
        dominant_eigenvalue=float(eigvals[0]),
        n_trials=n,
    )
