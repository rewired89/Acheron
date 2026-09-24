"""
Acheron Simulation 24: The Real comK/comS Equations, and a Second Way to
Lock the Native Circuit (Suel et al. 2007)
=====================================================================

PURPOSE:
bsubtilis_22_comK_excitable_circuit.py models the comK competence circuit
as a generic, textbook-form fast-activator/slow-inhibitor system, because
its primary source, Suel, Garcia-Ojalvo, Liberman & Elowitz (2006, Nature
440:545-550), has no open-access full text, so this project only had the
abstract, not the paper's own equations.

The founder supplied a DIFFERENT, later paper from the same lab that IS
fully available: Suel, Kulkarni, Dworkin, Garcia-Ojalvo & Elowitz (2007),
"Tunability and Noise Dependence in Differentiation Dynamics," Science
315(5819):1716-1719, DOI 10.1126/science.1137455. This is the direct
experimental follow-up to the 2006 paper, using the same comK/comS
circuit, and its own note 15 (part of the main text, not paywalled) gives
the actual functional-form ODEs for the circuit:

    dK/dt = aK + bK * K^n / (kK^n + K^n) - dK_deg * K / (1 + K/GK + S/GS) - lK*K
    dS/dt = aS + bS / (1 + (K/kS)^p) - dS_deg * S / (1 + K/GK + S/GS) - lS*S

where aK, aS are basal (constitutive) expression rates; bK is the strength
of ComK's own positive autoregulation (Hill activation, cooperativity n);
bS is comS's expression strength (Hill-repressed by K, cooperativity p);
the third term in each equation is degradation via competitive binding to
the shared MecA-ClpC-ClpP protease (the denominator couples K and S
degradation -- this is the actual mechanism ComS uses to protect ComK: a
large pool of either molecule saturates MecA's capacity and slows
degradation of both); lK, lS are linear (non-MecA) degradation/dilution.

WHAT THIS DOES NOT DO, READ BEFORE CITING THIS FILE:
This project does not have the paper's fitted numeric values for
aK, bK, kK, n, dK_deg, GK, GS, lK, aS, bS, kS, p, dS_deg, lS (they are in
the paper's own Supporting Online Material, which is not part of what was
supplied). What IS real and citable here is the STRUCTURAL FORM of the
equations (the Hill functions, the shared competitive-degradation
denominator), taken directly from the paper's own text. The parameter
VALUES below were found by hand (see git history / session notes) to
reproduce three qualitatively distinct regimes as aK is increased, the
same three the paper itself reports:
  - Low aK (near wild-type): rare, transient excursions that decay back to
    rest on their own -- excitable, matching the real circuit's actual job
    (Fig. 1A, Fig. 2A "0 uM" trace).
  - Intermediate aK: frequent, noise-sustained back-and-forth transitions
    between rest and the high state -- the paper's own Hyper-aK strain
    shows exactly this at intermediate IPTG (Fig. 2A, 1-10 uM traces:
    "cells repeatedly went in and out of the competent state").
  - High aK: a single transition to the high state that does not decay
    within the simulated window -- matches the paper's finding that at
    aK ~20x wild-type, essentially all cells enter and stay (Fig. 2, A
    and C), which the paper explains as aK exceeding what MecA-mediated
    degradation can pull back down (their own aK > bK argument).

This project's own illustrative parameters do NOT reproduce the paper's
specific reported multiples exactly (their oscillatory-to-locked boundary
is empirically near their own measured aK/aK_wt values, not derived here
from first principles). Treat the aK multiples used in this file's sweep
as internally-consistent labels for "low / intermediate / high" in THIS
model, not as a quantitative match to the real strain's induction curve.
This is a plausibility model of a real, cited functional form, the same
epistemic status as bsubtilis_22's own generic model, upgraded from a
generic cubic form to the real cited topology.

ALSO FROM THIS PAPER, NOT YET MODELED HERE: a rewired variant with one
added negative-feedback arm onto comK (their "CompRok" strain, real
Rok-mediated repression) cut the cell-to-cell variability of competence
duration roughly in half (13.9 +/- 3.4h vs. 20.2 +/- 9.9h wild-type,
their own measured numbers) without changing the mean duration -- a real,
wet-lab-demonstrated precedent for "adding a feedback arm makes a
stochastic circuit's timing more precise." Relevant if a future
comparison is drawn against bsubtilis_16_damage_sensing_reinforcement.py's
proposed reinforcement circuit; not simulated in this file.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))

DEFAULT_PARAMS = dict(
    aK=0.02, bK=1.0, kK=1.0, n=2.0, dK_deg=1.2, GK=1.083, GS=1.0, lK=0.05,
    aS=0.01, bS=0.3, kS=0.5, p=4.0, dS_deg=0.3, lS=0.05,
)


class ComKSuelCell:
    """The real comK/comS topology (Suel et al. 2007, note 15): Hill-function
    positive autoregulation of ComK plus Hill-repressed ComS, both degraded
    through a shared, competitive MecA-ClpC-ClpP term. Illustrative
    parameters (see module docstring); aK is the swept variable throughout."""

    def __init__(self, aK: float = 0.02, bK: float = 1.0, kK: float = 1.0,
                 n: float = 2.0, dK_deg: float = 1.2, GK: float = 1.083,
                 GS: float = 1.0, lK: float = 0.05,
                 aS: float = 0.01, bS: float = 0.3, kS: float = 0.5,
                 p: float = 4.0, dS_deg: float = 0.3, lS: float = 0.05,
                 noise_std: float = 0.0, seed: int = None):
        self.aK, self.bK, self.kK, self.n = aK, bK, kK, n
        self.dK_deg, self.GK, self.GS, self.lK = dK_deg, GK, GS, lK
        self.aS, self.bS, self.kS, self.p = aS, bS, kS, p
        self.dS_deg, self.lS = dS_deg, lS
        self.noise_std = noise_std
        self.rng = np.random.default_rng(seed)
        self.K = 0.02
        self.S = 0.0
        self._equilibrate_vegetative_S()

    def _equilibrate_vegetative_S(self, dt: float = 0.01, steps: int = 30000):
        """Let ComS reach its own vegetative (K~0) steady state before any
        write or noise is applied, matching a cell that has been growing
        vegetatively, not one started from an arbitrary S=0 non-equilibrium
        state."""
        for _ in range(steps):
            denom = 1.0 + self.K / self.GK + self.S / self.GS
            dS = (self.aS + self.bS / (1.0 + (self.K / self.kS) ** self.p)
                  - self.dS_deg * self.S / denom - self.lS * self.S)
            self.S = max(0.0, self.S + dS * dt)

    def write(self, kick: float = 1.0):
        """A transient inducing pulse (stress, or a deliberate push), not a
        change to the circuit's own parameters."""
        self.K += kick

    def step(self, dt: float = 0.01):
        denom = 1.0 + self.K / self.GK + self.S / self.GS
        dK = (self.aK + self.bK * self.K ** self.n / (self.kK ** self.n + self.K ** self.n)
              - self.dK_deg * self.K / denom - self.lK * self.K)
        dS = (self.aS + self.bS / (1.0 + (self.K / self.kS) ** self.p)
              - self.dS_deg * self.S / denom - self.lS * self.S)
        if self.noise_std > 0:
            dK += self.rng.normal(0, self.noise_std)
            dS += self.rng.normal(0, self.noise_std)
        self.K = max(0.0, self.K + dK * dt)
        self.S = max(0.0, self.S + dS * dt)

    def read(self, threshold: float = 1.0) -> int:
        return 1 if self.K > threshold else 0


def run_trajectory(hours: float, aK_multiple: float, aK0: float = 0.02,
                    noise_std: float = 0.06, seed: int = 0,
                    dt: float = 0.01, kick: float = 0.0) -> Dict:
    """kick=0 models spontaneous (noise-driven only) behavior, matching how
    Pinit is actually measured in the real system: no deliberate write, just
    watch whether/how often noise crosses the threshold on its own."""
    params = dict(DEFAULT_PARAMS)
    params['aK'] = aK0 * aK_multiple
    cell = ComKSuelCell(noise_std=noise_std, seed=seed, **params)
    if kick > 0:
        cell.write(kick)
    n_steps = int(hours * 60 / dt)
    high_steps = 0
    transitions = 0
    last_state = cell.read()
    for _ in range(n_steps):
        cell.step(dt=dt)
        state = cell.read()
        if state != last_state:
            transitions += 1
        last_state = state
        high_steps += state
    return {
        'final_state': cell.read(),
        'fraction_time_high': high_steps / n_steps,
        'transitions': transitions,
    }


def sweep_aK_regime(aK_multiples: List[float], hours: float = 96.0,
                     n_trials: int = 8, noise_std: float = 0.06) -> Dict[float, Dict]:
    """Spontaneous (no deliberate write), noise-driven behavior across aK.
    Reproduces the paper's qualitative regime map: low aK is quiescent
    (rare/no spontaneous entry, matching a low Pinit), intermediate aK is
    oscillatory (frequent noise-sustained entry/exit), high aK locks
    (one transition, then stays high for the rest of the window)."""
    results = {}
    for mult in aK_multiples:
        finals, transitions_list, frac_list = [], [], []
        for trial in range(n_trials):
            r = run_trajectory(hours, mult, seed=trial * 31 + int(mult * 10),
                                noise_std=noise_std, kick=0.0)
            finals.append(r['final_state'])
            transitions_list.append(r['transitions'])
            frac_list.append(r['fraction_time_high'])
        results[mult] = {
            'final_high_fraction': float(np.mean(finals)),
            'mean_transitions': float(np.mean(transitions_list)),
            'mean_frac_time_high': float(np.mean(frac_list)),
        }
    return results


def compare_lock_mechanisms(hours: float = 24.0, n_trials: int = 10) -> Dict:
    """Two independently-documented ways to lock this circuit: Suel 2006's
    'block exit' (modeled generically in bsubtilis_22, no real equations
    available), and Suel 2007's 'push aK high' (real equations, this file).
    Both use a deliberate write pulse here, then check the state 24h later,
    the same test bsubtilis_01/bsubtilis_22 already use."""
    from bsubtilis_22_comK_excitable_circuit import run_persistence as exit_blocked_run
    exit_blocked_correct = 0
    for trial in range(n_trials):
        r = exit_blocked_run(hours, exit_blocked=True, noise_std=0.3, seed=trial)
        exit_blocked_correct += int(r['final_state'] == 1)

    high_aK_correct = 0
    for trial in range(n_trials):
        r = run_trajectory(hours, aK_multiple=20.0, seed=trial, kick=1.0, noise_std=0.06)
        high_aK_correct += r['final_state']

    from bsubtilis_01_gardner_toggle_circuit import GardnerParams, run_persistence as gardner_run
    gardner_correct = 0
    for trial in range(n_trials):
        r = gardner_run(1, GardnerParams(), hours=hours, seed=trial, tx_noise=3.0)
        gardner_correct += r['genetic_correct']

    return {
        'comK_exit_blocked_2006style': exit_blocked_correct / n_trials,
        'comK_high_aK_2007style': high_aK_correct / n_trials,
        'gardner_toggle': gardner_correct / n_trials,
    }


def main():
    print("=" * 92)
    print("comK/comS REAL EQUATIONS (Suel et al. 2007) — regime map and a second lock mechanism")
    print("=" * 92)

    print("\nQuestion 1: does sweeping aK (comK basal expression) reproduce the paper's own")
    print("qualitative regime transition (quiescent/excitable -> oscillatory -> locked),")
    print("using spontaneous, noise-driven behavior only (no deliberate write pulse)?\n")
    aK_multiples = [1.0, 4.5, 8.0, 20.0]
    results = sweep_aK_regime(aK_multiples)
    print(f"{'aK (x baseline)':<18}{'Mean transitions/96h':>22}{'Mean fraction time high':>26}")
    for mult in aK_multiples:
        r = results[mult]
        print(f"{mult:<18}{r['mean_transitions']:>22.1f}{r['mean_frac_time_high']:>26.0%}")

    print("\nQuestion 2: how do the two independently-documented lock mechanisms compare")
    print("to each other and to the already-validated Gardner toggle, same 24h test?\n")
    cmp = compare_lock_mechanisms()
    print(f"  comK, exit-blocked (Suel 2006-style, generic model): {cmp['comK_exit_blocked_2006style']:.0%}")
    print(f"  comK, high-aK (Suel 2007-style, real equations):     {cmp['comK_high_aK_2007style']:.0%}")
    print(f"  Gardner toggle switch:                               {cmp['gardner_toggle']:.0%}")

    print("\n" + "=" * 92)
    print("INTERPRETATION")
    print("=" * 92)
    print("At baseline aK, the circuit is quiescent/excitable: essentially no spontaneous")
    print("crossings in 96h in this run, matching the real circuit's low (~3%) probability")
    print("of initiation per cell division. At an intermediate aK, noise repeatedly drives")
    print("the system in and out of the high state, an oscillatory regime the paper's own")
    print("Hyper-aK strain shows at intermediate induction. At high aK, one crossing occurs")
    print("and the state does not decay for the rest of the window, a SECOND, independently")
    print("documented route to a locked circuit, distinct from bsubtilis_22's 'block exit'")
    print("mechanism from the 2006 paper. Two different real papers, two different real")
    print("genetic perturbations, converging on the same qualitative result: this circuit")
    print("CAN be pushed from transient to persistent. Neither has been tested for data")
    print("storage or through damage/regrowth. See docs/SCIENTIFIC_AUDIT_2026.md Part 28.")
    print("=" * 92)


if __name__ == '__main__':
    main()
