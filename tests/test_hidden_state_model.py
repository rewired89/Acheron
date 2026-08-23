"""Tests for analysis/hidden_state_model.py.

The reference values below were obtained by actually running tasmorpho's
own script (github.com/marcelbtec/tasmorpho, 03_reduced_count_fit.py,
unmodified) in this environment and reading its printed output — not
transcribed from the README. This is a numerical cross-validation against
the original implementation, not just an internal self-consistency check.
"""

import numpy as np
import pytest

from analysis.hidden_state_model import (
    PARAM_NAMES,
    closed_form_estimate,
    fit,
    p_challenge_given_sh,
    p_immediate,
    phi_cdf,
    phi_inv,
)

# From an actual run of tasmorpho/scripts/03_reduced_count_fit.py
REFERENCE_PARAMS = {
    "mu_8OH": -0.675863,
    "mu_nigericin": -1.13214,
    "mu_monensin": -1.1572,
    "theta_ch": -0.483831,
}
REFERENCE_NIGERICIN_CHALLENGE = 0.148764
REFERENCE_MONENSIN_CHALLENGE = 0.144638


def test_phi_cdf_and_inv_are_inverses():
    for x in (-2.0, -0.5, 0.0, 0.5, 2.0):
        assert phi_inv(phi_cdf(x)) == pytest.approx(x, abs=1e-8)


def test_closed_form_matches_tasmorpho_reference():
    xhat = closed_form_estimate()
    for name, expected in zip(PARAM_NAMES, xhat):
        assert expected == pytest.approx(REFERENCE_PARAMS[name], abs=1e-4)


def test_full_fit_matches_tasmorpho_reference():
    result = fit()
    for name, val in zip(PARAM_NAMES, result.params):
        assert val == pytest.approx(REFERENCE_PARAMS[name], abs=1e-4)


def test_held_out_predictions_match_tasmorpho_reference():
    """The whole point of the model: held-out challenge-penetrance
    predictions for drugs whose challenge data was never used in fitting."""
    result = fit()
    nig_est = result.held_out_nigericin_challenge[0]
    mon_est = result.held_out_monensin_challenge[0]
    assert nig_est == pytest.approx(REFERENCE_NIGERICIN_CHALLENGE, abs=1e-4)
    assert mon_est == pytest.approx(REFERENCE_MONENSIN_CHALLENGE, abs=1e-4)


def test_probability_helpers_are_well_formed_probabilities():
    for mu in (-2.0, -0.5, 0.0, 0.5, 2.0):
        p = p_immediate(mu)
        assert 0.0 <= p <= 1.0
    for mu, theta in ((-1.0, -0.5), (0.0, 0.0), (-2.0, 1.0)):
        p = p_challenge_given_sh(mu, theta)
        assert 0.0 <= p <= 1.0
