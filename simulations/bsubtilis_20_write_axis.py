"""
Acheron Experiment: Dominant Write-Axis Analysis on the Gardner Toggle
Circuit
=============================================================================

QUESTION:
Of the ways you could perturb the Gardner toggle circuit to write a bit
(nudge alpha1, nudge alpha2, change the promoter strength_ratio), which
direction writes the persistent voltage-readout state most efficiently per
unit of injected energy? Acheron's own manifest (MANIFEST.md, Section 2)
defines SET_BIT as "force local bioelectric state via stimulation... no
operation may be assumed possible unless a measurable physical mechanism
exists" — this experiment computes that efficient-write direction directly
from the simulated mechanism instead of assuming a knob is efficient.

METHODOLOGY (see analysis/memory_geometry.py for full attribution):
Q / R / K_mem = R Q^-1 R^T write-axis geometry, generalized from
tasmorpho's script 01 (github.com/marcelbtec/tasmorpho, MIT), which
computes this from BETSE tissue-simulator perturbation trials. Here the
"trials" come directly from GardnerToggleCell instead of BETSE.

PERTURBATION SPACE (analogous to tasmorpho's na/k/gj perturbation cases):
  dim 0: delta_alpha1        (promoter 1 strength nudge)
  dim 1: delta_alpha2        (promoter 2 strength nudge)
  dim 2: delta_strength_ratio (promoter mismatch nudge)

ENERGY COST PROXY:
Sum of squared parameter deltas (a simple, explicit proxy — GardnerToggleCell
does not track a physical energy unit, unlike BETSE's ion-flux accounting
that tasmorpho's Q matrix uses). This is flagged deliberately: a real Q
would need an actual metabolic/transcriptional cost model, which does not
exist in this repository yet. Treat Q here as illustrative of the METHOD,
not a validated energy cost.

OBSERVABLE:
Mean cell.V over the last hour of a 24h run STARTING FROM THE NEUTRAL,
UNWRITTEN STATE (no cell.write() pulse) with only the parameter
perturbation applied — analogous to tasmorpho perturbing a baseline/
control condition, not perturbing on top of an already-committed write.
(A first version of this script applied write(1) THEN perturbed
parameters; that overwhelms any parameter-level effect entirely — the
write(1) kick sets u=alpha1≈50, v=0, which dominates modest alpha
perturbations of order ±8, so every trial's shift came out exactly 0.
That was a real design bug, not a finding — caught by checking the raw
per-trial shift values before trusting the fitted K_mem, rather than
reporting the degenerate all-zero result at face value.)

FINDING ALREADY VISIBLE FROM A DIRECT PROBE (see main() below):
Because this is a Gardner-style toggle switch with Hill cooperativity
beta=gamma=2 — Gardner et al.'s own demonstrated ULTRASENSITIVE bistable
regime, i.e. designed to behave like a sharp digital switch, not a graded
analog memory — the observable is close to a step function of the
perturbation, not the smoothly graded response tasmorpho's continuous
BETSE tissue models. Expect K_mem's linear write-map assumption to fit
this substrate poorly; that mismatch is itself the reportable result, and
this script also runs a direct threshold-crossing search per perturbation
axis as the well-posed alternative question for a digital substrate: "how
large a nudge is needed to guarantee a flip?"

WHAT THIS DOES NOT DO:
This characterizes *this specific simulated model with an illustrative
cost proxy* — it is a method demonstration, not a claim about which real
induction chemical (xylose vs. IPTG vs. a promoter-strength genetic
redesign) is cheapest in a real cell.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from analysis.memory_geometry import PerturbationTrial, compute_write_axis
from simulations.bsubtilis_01_gardner_toggle_circuit import GardnerParams, GardnerToggleCell

DIM_NAMES = ("delta_alpha1", "delta_alpha2", "delta_strength_ratio")


def _make_perturbed_params(base_params: GardnerParams, delta: np.ndarray) -> GardnerParams:
    return GardnerParams(
        alpha1=base_params.alpha1 + delta[0],
        alpha2=base_params.alpha2 + delta[1],
        strength_ratio=max(0.01, base_params.strength_ratio + delta[2]),
    )


def _settled_mean_V(params: GardnerParams, hours: float, seed: int) -> float:
    """Run from the neutral, unwritten state (u=v=0, no write() pulse) —
    the perturbation itself is the only thing breaking symmetry, matching
    tasmorpho's setup of perturbing a baseline/control condition."""
    cell = GardnerToggleCell(params, seed=seed, transcriptional_noise_std=0.0)
    n_steps = int(hours * 60 / 1.0)
    vs = []
    for i in range(n_steps):
        cell.step(dt=0.02)
        if i >= n_steps - 60:  # last simulated hour
            vs.append(cell.V)
    return float(np.mean(vs))


def run_trial(delta: np.ndarray, base_params: GardnerParams, hours: float = 24.0, seed: int = 0) -> PerturbationTrial:
    """Perturb the circuit's parameters (no write() pulse), run for `hours`
    from the neutral state, and measure the resulting shift in mean settled
    voltage relative to an unperturbed baseline circuit."""
    perturbed = _make_perturbed_params(base_params, delta)
    baseline_V = _settled_mean_V(base_params, hours, seed)
    perturbed_V = _settled_mean_V(perturbed, hours, seed)
    shift = np.array([perturbed_V - baseline_V])
    cost = float(np.sum(delta ** 2))  # illustrative proxy -- see module docstring

    return PerturbationTrial(perturbation=delta, energy_cost=cost, observable_shift=shift)


KNIFE_EDGE_PROBE = 1e-6  # far below any plausible real perturbation


def _search_direction(
    dim: int, sign: float, base_params: GardnerParams, base_V: float, hours: float, seed: int,
    search_hi: float, tol: float,
) -> float:
    """Binary-search the smallest |magnitude| along one signed direction of
    one axis that flips the settled state. Returns +inf if no flip occurs
    within search_hi in this direction, or 0.0 if even a microscopic probe
    (KNIFE_EDGE_PROBE) already flips it — i.e. the real threshold is below
    what a finite search can resolve, not equal to wherever the bisection
    tolerance happens to bottom out."""

    def flipped(mag: float) -> bool:
        delta = np.zeros(3)
        delta[dim] = sign * mag
        v = _settled_mean_V(_make_perturbed_params(base_params, delta), hours, seed)
        return abs(v - base_V) > 20.0  # well above noise floor, well below the ~70mV jump

    if not flipped(search_hi):
        return float("inf")

    if flipped(KNIFE_EDGE_PROBE):
        # Don't report the bisection's tolerance floor as if it were the
        # real threshold -- it isn't. The true threshold is at or below
        # this microscopic probe.
        return 0.0

    lo, hi = KNIFE_EDGE_PROBE, search_hi
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if flipped(mid):
            hi = mid
        else:
            lo = mid
    return hi


def find_flip_threshold(
    dim: int, base_params: GardnerParams, hours: float = 24.0, seed: int = 0,
    search_hi: float = 20.0, tol: float = 0.05,
) -> float:
    """Binary-search the smallest perturbation magnitude along one axis
    (checking BOTH the positive and negative direction, since which sign
    favors a flip depends on which basin the baseline already sits in --
    e.g. increasing alpha2 reinforces a v-dominant baseline rather than
    flipping it) that flips the settled state — the well-posed question for
    a digital (strongly bistable) substrate, where a linear write-map is a
    poor local model. Returns the critical magnitude (smaller of the two
    directions), or +inf if neither direction flips within search_hi."""
    base_V = _settled_mean_V(base_params, hours, seed)
    pos = _search_direction(dim, +1.0, base_params, base_V, hours, seed, search_hi, tol)
    neg = _search_direction(dim, -1.0, base_params, base_V, hours, seed, search_hi, tol)
    return min(pos, neg)


def main() -> None:
    print("=" * 72)
    print("DOMINANT WRITE-AXIS ANALYSIS — Gardner Toggle Circuit")
    print("=" * 72)

    base_params = GardnerParams()
    rng = np.random.default_rng(0)

    trials = []
    n_trials = 60
    for i in range(n_trials):
        delta = rng.normal(scale=[8.0, 8.0, 0.4], size=3)
        trials.append(run_trial(delta, base_params, hours=24.0, seed=i))

    shifts = np.array([t.observable_shift[0] for t in trials])
    n_near_zero = int(np.sum(np.abs(shifts) < 5.0))
    n_flipped = int(np.sum(np.abs(shifts) > 20.0))
    print(f"Ran {len(trials)} perturbation trials across dims {DIM_NAMES}")
    print(f"Observable shift distribution: {n_near_zero} near 0 mV, {n_flipped} large "
          f"(~{np.abs(shifts[np.abs(shifts) > 20]).mean():.0f} mV) jumps"
          if n_flipped else f"Observable shift distribution: {n_near_zero} near 0 mV, 0 large jumps")

    result = compute_write_axis(trials)
    print(f"\nK_mem eigenvalues: {result.eigenvalues}")
    print("R (fitted linear write map, mV per unit):", dict(zip(DIM_NAMES, result.R[0].round(3))))

    is_bimodal = n_flipped > 0 and n_near_zero > 0
    if is_bimodal:
        print("\n>>> Observable is BIMODAL (near-0 or a ~70mV jump, nothing in")
        print("    between) rather than continuously graded -- a linear R/K_mem")
        print("    fit is not a meaningful local model here. This is the reportable")
        print("    finding for this substrate class, not a failed computation; see")
        print("    the threshold-crossing scan below for the well-posed alternative.")

    print("\n" + "-" * 72)
    print("THRESHOLD-CROSSING SCAN (well-posed for a bistable/digital substrate)")
    print("-" * 72)
    print("Smallest single-axis perturbation magnitude (either sign) that flips the settled state:")
    thresholds = {}
    for dim, name in enumerate(DIM_NAMES):
        thr = find_flip_threshold(dim, base_params, hours=24.0, seed=0)
        thresholds[name] = thr
        if thr == 0.0:
            thr_str = f"< {KNIFE_EDGE_PROBE:g} (knife-edge -- even a microscopic nudge flips it)"
        elif np.isfinite(thr):
            thr_str = f"{thr:.3f}"
        else:
            thr_str = "no flip found up to search_hi"
        print(f"  {name:<24} critical magnitude = {thr_str}")

    cheapest = min(thresholds, key=lambda k: thresholds[k])

    print("\n" + "=" * 72)
    print("INTERPRETATION")
    print("=" * 72)
    if is_bimodal:
        print("The random-perturbation K_mem fit is degenerate (as expected for a")
        print("  Hill-cooperativity-2 toggle switch — Gardner's own demonstrated")
        print("  ULTRASENSITIVE regime, designed to be a sharp digital switch, not a")
        print("  graded analog memory like the continuous Vmem gradients tasmorpho's")
        print("  BETSE-based method targets). Applying a continuous-tissue write-map")
        print("  framework unmodified to a synthetic bistable switch is the wrong")
        print("  tool for this substrate class -- the threshold-crossing scan above")
        print("  is the correctly-posed question instead.")
    if all(t == 0.0 for t in thresholds.values()):
        print(f"\nAll three axes are knife-edge: at this exactly-symmetric baseline")
        print(f"  (alpha1=alpha2, strength_ratio=1, transcriptional_noise_std=0), a")
        print(f"  perturbation as small as {KNIFE_EDGE_PROBE:g} units already determines the")
        print(f"  full 24h outcome deterministically. There is no 'cheapest axis' to")
        print(f"  report -- all three are equally free at this baseline, because the")
        print(f"  baseline itself sits exactly on the unstable separatrix between the")
        print(f"  two basins. In a real cell, thermal/transcriptional noise (which")
        print(f"  this run deliberately set to 0 to isolate the parameter effect)")
        print(f"  would settle the outcome on its own before any control input got")
        print(f"  the chance to -- i.e. an exactly-symmetric design is not a usable")
        print(f"  SET_BIT baseline; a real device needs either an intentional")
        print(f"  built-in asymmetry or an explicit write() pulse (as gardner_toggle_")
        print(f"  circuit.py's own persistence tests already use) to be controllable.")
    else:
        print(f"\nCheapest single-axis flip (smallest critical magnitude): '{cheapest}'")
        print(f"  = {thresholds[cheapest]:.3f} units to guarantee a bit flip in this model.")
        print("This threshold is measured directly from the simulator at the stated")
        print("  seed/hours, not invented; rerunning with a different seed or noise")
        print("  level would shift it somewhat, exactly like any other simulation")
        print("  result in this repository.")
    print("=" * 72)


if __name__ == "__main__":
    main()
