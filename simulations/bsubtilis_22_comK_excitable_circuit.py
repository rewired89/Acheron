"""
Acheron Simulation 17: The comK Excitable Circuit, B. subtilis's Own Native
Alternative to an Imported Toggle Switch
=====================================================================

PURPOSE:
docs/SCIENTIFIC_AUDIT_2026.md Part 27 traces a real research thread back from
a Scientific American / Quanta Magazine piece on noise in gene expression
(Elowitz's lab) to a primary paper this project hadn't cited before:

Sueel, Garcia-Ojalvo, Liberman & Elowitz (2006), "An excitable gene
regulatory circuit induces transient cellular differentiation," Nature
440(7083):545-550, DOI 10.1038/nature04588, PMID 16554821.

That paper is about comK, the gene circuit that controls competence
(DNA uptake) in B. subtilis. Two facts from its abstract matter directly
here:

1. It is a REAL, NATIVE B. subtilis circuit, not imported from E. coli the
   way bsubtilis_01_gardner_toggle_circuit.py's Gardner-topology switch is. It already
   works, reliably, inside the exact organism this project targets.
2. Structurally it is EXCITABLE, not bistable: positive feedback (ComK
   promotes its own expression) plus a slower negative feedback (an exit
   pathway) that eventually returns the cell to vegetative growth. Noise
   is what triggers entry; the circuit's own dynamics govern the return.
   The abstract explicitly reports the authors "re-engineered the gene
   circuit to specifically block exit" as a test of their model, i.e. they
   demonstrated, in real B. subtilis, that disabling the negative-feedback
   arm converts a transient noise-driven pulse into a state the cell does
   not spontaneously leave.

That second fact is the one worth simulating: it is a wet-lab-demonstrated
precedent, in the right organism, for turning a noise-driven excitable
circuit into something closer to the persistent memory this project needs,
which is a different and arguably better-grounded starting point than
importing a bistable topology from a different organism.

WHAT THIS DOES:
Models the topology described above in the minimal standard mathematical
form for a two-variable excitable system (fast self-activating variable +
slower delayed inhibitor), the same general class of model the paper's own
abstract describes qualitatively ("excitable core module containing
positive and negative feedback loops"). Two variants are compared:
  - NORMAL: both feedback arms active, matching the native circuit.
  - EXIT-BLOCKED: the negative-feedback (exit) term is disabled after a
    write pulse, matching the paper's own re-engineering test.

WHAT THIS DOES NOT DO, READ BEFORE CITING THIS FILE:
This is NOT the paper's own fitted model. Süel et al. 2006 is a Nature
paper with no open-access full text available to this project (checked via
PubMed Central, no PMCID exists for PMID 16554821), so this project has
only the abstract, not their specific equations, rate constants, or
measured parameter values. The equations below are a generic,
textbook-standard excitable-system form (structurally the same class used
throughout mathematical biology for exactly this kind of circuit, e.g.
FitzHugh-Nagumo-style fast-activator/slow-inhibitor dynamics), chosen to
reproduce the QUALITATIVE behavior the abstract describes (spontaneous
noise-triggered pulses; exit-blocking converts pulses to a locked state).
No number in this file should be read as a measured B. subtilis value.
This is a plausibility model, not a validated circuit, the same epistemic
status bsubtilis_01_gardner_toggle_circuit.py's own hypothetical voltage-output link
carries, stated with the same explicitness.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerToggleCell


class ComKExcitableCell:
    """Fast activator (K, ComK-like) + slow inhibitor (S, exit-pathway-like).

    dK/dt = (K - K^3/3 - S + drive + noise) / tau_fast
    dS/dt = exit_gain * (K - gamma * S) / tau_slow

    exit_gain = 0 reproduces the paper's "block exit" re-engineering: the
    negative feedback arm is disabled, so nothing pulls K back down once
    noise (or a deliberate write pulse) pushes it over threshold.
    """

    K_LOW, K_HIGH = -1.2, 1.8   # dimensionless activator bounds (vegetative / competent-like)

    def __init__(self, tau_fast: float = 1.0, tau_slow: float = 12.5,
                 gamma: float = 0.8, exit_gain: float = 1.0,
                 noise_std: float = 0.0, seed: int = None):
        self.tau_fast = tau_fast
        self.tau_slow = tau_slow
        self.gamma = gamma
        self.exit_gain = exit_gain
        self.noise_std = noise_std
        self.rng = np.random.default_rng(seed)
        self.K = self.K_LOW
        self.S = 0.0

    def write(self, kick: float = 3.0):
        """A transient inducing pulse (matches the real trigger: stress or
        a deliberate optogenetic/chemical push), not a permanent drive."""
        self.K = self.K_LOW + kick

    def step(self, dt: float = 0.05):
        drive = self.rng.normal(0, self.noise_std) if self.noise_std > 0 else 0.0
        dK = (self.K - (self.K ** 3) / 3.0 - self.S + drive) / self.tau_fast
        dS = self.exit_gain * (self.K - self.gamma * self.S) / self.tau_slow
        self.K += dK * dt
        self.S += dS * dt

    def read(self) -> int:
        return 1 if self.K > 0.0 else 0


def run_persistence(hours: float, exit_blocked: bool, noise_std: float,
                     seed: int = 0, dt: float = 0.05) -> Dict:
    cell = ComKExcitableCell(exit_gain=0.0 if exit_blocked else 1.0,
                              noise_std=noise_std, seed=seed)
    cell.write()
    n_steps = int(hours * 60 / dt)
    high_steps = 0
    for _ in range(n_steps):
        cell.step(dt=dt)
        high_steps += int(cell.read() == 1)
    return {
        'final_state': cell.read(),
        'fraction_time_high': high_steps / n_steps,
    }


def sweep_persistence(hours_list: List[float], noise_std: float = 0.3,
                       n_trials: int = 8) -> Dict[str, Dict[float, Dict]]:
    results = {'normal (excitable, exit active)': {}, 'exit-blocked (locked)': {}}
    for hours in hours_list:
        for blocked, label in [(False, 'normal (excitable, exit active)'),
                                (True, 'exit-blocked (locked)')]:
            final_high, frac_sum = 0, 0.0
            for trial in range(n_trials):
                r = run_persistence(hours, blocked, noise_std, seed=trial * 17 + int(hours))
                final_high += r['final_state']
                frac_sum += r['fraction_time_high']
            results[label][hours] = {
                'final_high_fraction': final_high / n_trials,
                'mean_time_high': frac_sum / n_trials,
            }
    return results


def compare_to_gardner_toggle(hours: float = 24.0, n_trials: int = 8) -> Dict:
    """Same persistence question (write a '1', check it 24h later), run
    against both the exit-blocked comK model here and the already-validated
    Gardner toggle (bsubtilis_01_gardner_toggle_circuit.py, imported unmodified) at its
    default matched-promoter parameters, for a direct side-by-side."""
    comk_correct = 0
    for trial in range(n_trials):
        r = run_persistence(hours, exit_blocked=True, noise_std=0.3, seed=trial)
        comk_correct += int(r['final_state'] == 1)

    from bsubtilis_01_gardner_toggle_circuit import GardnerParams, run_persistence as gardner_run
    gardner_correct = 0
    for trial in range(n_trials):
        r = gardner_run(1, GardnerParams(), hours=hours, seed=trial, tx_noise=3.0)
        gardner_correct += r['genetic_correct']

    return {
        'comK_exit_blocked_fidelity': comk_correct / n_trials,
        'gardner_toggle_fidelity': gardner_correct / n_trials,
    }


def main():
    print("=" * 88)
    print("comK EXCITABLE CIRCUIT — native B. subtilis alternative to the imported Gardner switch")
    print("=" * 88)
    print("\nQuestion 1: does blocking the exit arm turn a transient pulse into a lasting state?\n")

    hours_list = [1.0, 6.0, 24.0]
    results = sweep_persistence(hours_list, noise_std=0.3, n_trials=8)
    print(f"{'Hours after write':<20}{'Normal: still high':>22}{'Exit-blocked: still high':>28}")
    for hours in hours_list:
        normal = results['normal (excitable, exit active)'][hours]['final_high_fraction']
        blocked = results['exit-blocked (locked)'][hours]['final_high_fraction']
        print(f"{hours:<20}{normal:>21.0%}{blocked:>29.0%}")

    print("\nQuestion 2: how does the exit-blocked comK model compare to the already-")
    print("validated Gardner toggle switch on the exact same 24h persistence test?\n")
    cmp = compare_to_gardner_toggle()
    print(f"  comK (exit-blocked):    {cmp['comK_exit_blocked_fidelity']:.0%}")
    print(f"  Gardner toggle switch:  {cmp['gardner_toggle_fidelity']:.0%}")

    print("\n" + "=" * 88)
    print("INTERPRETATION")
    print("=" * 88)
    print("In the NORMAL circuit, noise triggers entry but the slow negative-feedback arm")
    print("still pulls the state back down, transient by design, matching the real comK")
    print("circuit's actual job (a temporary competence window, not permanent memory).")
    print("Blocking that arm (exit_gain=0) is the same qualitative move Sueel et al. 2006")
    print("made experimentally in real B. subtilis to test their model. Here it produces a")
    print("state that does not spontaneously decay, which is the property this project's")
    print("storage design needs.")
    print("\nThis is NOT evidence the comK approach is validated for data storage. Nobody has")
    print("built an exit-blocked comK variant for that purpose, or tested it through damage")
    print("and regrowth. It IS evidence that a real, native, already-working B. subtilis")
    print("circuit can be pushed from excitable to locked with a single, previously")
    print("demonstrated modification, which is a different and arguably stronger starting")
    print("point than importing an E. coli-measured topology, see docs/SCIENTIFIC_AUDIT_2026.md")
    print("Part 27 for the full citation and caveats.")
    print("=" * 88)


if __name__ == '__main__':
    main()
