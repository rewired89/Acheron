"""
Acheron Simulation 24: Phase-Encoded Readout - Using the Native Oscillation
as the Carrier Instead of Fighting It
================================================================================

STATUS (added after audit Part 26): THIS FILE IS A SENSITIVITY ANALYSIS UNDER
AN ASSUMED COUPLING, NOT A PREDICTION. The in-phase / anti-phase behavior of
the two bit values is imposed by hand (see "WHAT THIS FILE IS NOT", item 3),
and bsubtilis_21_optical_write_replication.py could not derive that
anti-phase from the potassium mechanism Yang et al. describe, in a 12-point
parameter sweep, for a structural reason. The accuracy figures below are
therefore properties of the assumption, and say nothing about whether a real
cell would behave this way. Phase encoding stands on their published
experiment plus an assumed coupling, with no working mechanistic model in
this repository behind it.

PURPOSE:
Five prior files in this project (bsubtilis_08_native_oscillation_interference.py,
bsubtilis_09_eis_readout_interference.py, bsubtilis_11_phase_locked_readout.py,
bsubtilis_12_decoupled_channel_readout.py, bsubtilis_14_voltage_colony_regrowth.py, audit Parts 12,
13, 17, 18, 21) all treat the B. subtilis biofilm's native potassium-wave
oscillation as NOISE: something that corrupts a voltage readout and has
to be averaged out, timed around, or engineered away. This file tests the
opposite framing, which came from a real published result this project
had not previously cited.

THE PAPER THIS COMES FROM:
Yang, Bialecka-Fornal, Weatherwax, Larkin, Prindle, Liu, Garcia-Ojalvo &
Suel (2020), "Encoding membrane potential-based memory within a microbial
community," Cell Systems 10(5):417-423, DOI 10.1016/j.cels.2020.04.002,
PMID 32343961, PMC7286314. Same lab as Prindle et al. 2015, same strain
(NCIB 3610), same channel (yugO).

What they actually did, from the paper's own text:
- A 5-second blue light (438 nm) exposure to a region of a living biofilm
  persistently changes those cells' membrane potential, confirmed with the
  Nernstian dye ThT at 10 uM.
- The mechanism is yugO-specific: a delta-yugO deletion strain shows no
  noticeable membrane potential change on light exposure, and excess
  extracellular potassium (but not sodium) blocks the response.
- Their model's interpretation: light leaves a fraction of yugO channel
  subunits permanently in the conducting state, so exposed cells PASSIVELY
  follow extracellular potassium, while unexposed cells retain active
  control of their channels and counter-regulate.
- The consequence, and the part that matters here: exposed and unexposed
  cells respond to potassium oscillations in ANTI-PHASE. Cross-correlation
  is anti-correlated at zero lag and maximally correlated at 50 minutes
  lag, half of their imposed 100-minute period. This held against both an
  artificially imposed oscillation (alternating 150 mM and 8 mM external
  potassium) and the biofilm's own natural one.
- The pattern stayed readable at single-cell resolution for over 3 hours.
- Their own discussion frames this for biological computing: the anti-phase
  behavior "allows us to produce a clear signal that is either 'on' or
  'off,' as in traditional digital memory."

THE IDEA THIS FILE TESTS:
If a stored bit sets whether a cell RESPONDS IN PHASE OR ANTI-PHASE to the
ambient oscillation, rather than setting a static voltage level, then the
oscillation stops being interference and becomes a carrier wave, the way a
radio station needs a carrier to modulate. The readout becomes a
correlation between the cell's voltage trace and a reference trace, and the
sign of that correlation is the bit.

The concrete, falsifiable prediction that separates the two schemes:
- LEVEL encoding (this project's existing scheme) gets WORSE as the
  oscillation amplitude grows. Already established, audit Parts 12 and 13.
- PHASE encoding should get BETTER as the oscillation amplitude grows, and
  should fail completely at zero amplitude, because with no carrier there
  is nothing to be in phase with.

If the run shows that inversion, the two schemes have opposite failure
modes and the choice between them depends on a measurement nobody has made
yet (how big the native swing actually is).

WHAT THIS FILE IS NOT, STATED PLAINLY:
1. Suel et al.'s memory is NOT a genetic circuit. It is a persistent
   protein-level modification of existing yugO channels, and their own
   discussion says so explicitly ("does not arise from positive feedback,
   but rather from enduring modifications at the protein level"). Wiring a
   Gardner toggle's genetic state to a cell's in-phase versus anti-phase
   potassium response has never been built or measured by anyone. It is
   the same category of unbuilt link as bsubtilis_01_gardner_toggle_circuit.py's
   original repressor-to-ion-channel proposal, not a validated mechanism.
2. This file does NOT reimplement the paper's Hodgkin-Huxley model. It
   keeps this project's own already-used dynamics (the Gardner ODE for the
   genetic state, the same first-order voltage tracking and the same noise
   magnitudes as bsubtilis_01_gardner_toggle_circuit.py) and only changes what the
   voltage is tracking. That keeps the comparison against the existing
   level-encoding files apples-to-apples, which reimplementing their model
   would not.
3. The sign flip (in-phase for bit 1, anti-phase for bit 0) is a
   phenomenological stand-in for their passive-versus-active channel
   control, not their equations.
4. Measurement noise on a real ThT imaging read has no citation in this
   project, so it is SWEPT here rather than assigned a value, per
   docs/THIRD_PARTY_METHODS.md's no-numeric-invention rule.
5. Protein-level memory of the kind Suel et al. demonstrate would be
   diluted away by cell division. Their own discussion notes biofilm cells
   are "predominantly non-replicating," which is part of why it persists.
   So this is proposed here as a READOUT for a genetically stored bit,
   which does survive division (audit Parts 8, 20, 22), not as a
   replacement storage mechanism.

A BOOTSTRAPPING PROBLEM THIS AVOIDS, UNLIKE PART 17:
bsubtilis_11_phase_locked_readout.py needed to PREDICT the oscillation's phase on a
schedule, and its own docstring flagged that you cannot get the phase
without already having a working readout. Phase encoding needs something
different and weaker: a simultaneous REFERENCE measurement, which is what
Suel et al. actually had (an unexposed region of the same biofilm, and
direct microfluidic control of the external potassium). Measuring a
reference is not the same problem as predicting a schedule.
"""

import os
import sys
from typing import Dict, List

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from bsubtilis_01_gardner_toggle_circuit import GardnerParams, GardnerToggleCell
from bsubtilis_08_native_oscillation_interference import ambient_oscillation_offset

SAMPLE_EVERY_MIN = 5.0    # Suel et al. imaged every 5-15 min; 5 is their finer cadence
DEFAULT_PERIOD_H = 3.0    # mid-range of the documented 2-4h native period (Parts 12-13)


class PhaseEncodedCell(GardnerToggleCell):
    """Same Gardner repressor circuit and same noise magnitudes as the
    parent. The one change: the stored bit no longer selects a static
    target voltage (V_HIGH vs V_LOW). It selects the SIGN of the cell's
    response to the ambient oscillation, modeling Suel et al.'s passive
    (light-exposed, follows external potassium) versus active (unexposed,
    counter-regulates) cell types. Both bit values sit at the same mean
    voltage, so absolute voltage carries no information at all in this
    scheme, by construction."""

    def __init__(self, params: GardnerParams, seed: int = None,
                 transcriptional_noise_std: float = 0.0,
                 channel_noise_std: float = 5.0,
                 thermal_noise_std: float = 0.4,
                 response_fraction: float = 1.0):
        super().__init__(params, seed=seed,
                         transcriptional_noise_std=transcriptional_noise_std,
                         channel_noise_std=channel_noise_std,
                         thermal_noise_std=thermal_noise_std)
        # How much of the ambient swing the cell reproduces. 1.0 = follows it
        # fully. Unmeasured, so the default is the simple case and callers
        # can sweep it.
        self.response_fraction = response_fraction
        self.V = self.V_REST

    def step_phase(self, t_minutes: float, amplitude_mv: float,
                   period_hours: float, dt: float = 0.02):
        """Advance the genetic state with the parent's validated ODE, then
        drive the voltage toward a target that oscillates in phase or in
        anti-phase with the ambient signal, depending on the stored bit."""
        # Parent step advances u/v exactly as every other file in this
        # project does. Its own voltage update is overwritten below.
        v_before = self.V
        super().step(dt=dt)
        self.V = v_before

        reference = ambient_oscillation_offset(t_minutes, amplitude_mv, period_hours)
        gain = 1.0 if self.u > self.v else -1.0
        target_V = self.V_REST + gain * self.response_fraction * reference

        dV = (target_V - self.V) * 0.05 * dt * 100   # same tracking rate as the parent
        dV += self.rng.normal(0, self.channel_noise * np.sqrt(dt))
        dV += self.rng.normal(0, self.thermal_noise * np.sqrt(dt))
        self.V = float(np.clip(self.V + dV, -120, 60))


def phase_read(voltage_samples: List[float], reference_samples: List[float]) -> int:
    """Correlate the cell's sampled voltage against the reference trace.
    Positive correlation reads as 1 (in phase), negative as 0 (anti-phase).
    This is the discrete stand-in for the cross-correlation Suel et al.
    actually computed between exposed and unexposed biofilm regions."""
    v = np.asarray(voltage_samples, dtype=float)
    r = np.asarray(reference_samples, dtype=float)
    if len(v) < 2 or np.std(v) == 0 or np.std(r) == 0:
        return 0
    corr = float(np.corrcoef(v, r)[0, 1])
    if not np.isfinite(corr):
        return 0
    return 1 if corr > 0 else 0


def run_phase_trial(bit: int, amplitude_mv: float, period_hours: float,
                    seed: int, window_min: float, measurement_noise_std: float,
                    settle_min: float = 60.0,
                    params: GardnerParams = None,
                    tx_noise: float = 3.0,
                    response_fraction: float = 1.0) -> int:
    """Write a bit, let the circuit settle, then take one phase read over
    `window_min` minutes. Returns 1 if the read was correct."""
    params = params or GardnerParams()
    cell = PhaseEncodedCell(params, seed=seed, transcriptional_noise_std=tx_noise,
                            response_fraction=response_fraction)
    cell.write(bit)
    rng = np.random.default_rng(seed + 7919)

    t = 0.0
    for _ in range(int(settle_min)):
        t += 1.0
        cell.step_phase(t, amplitude_mv, period_hours)

    v_samples, r_samples = [], []
    next_sample = SAMPLE_EVERY_MIN
    for _ in range(int(window_min)):
        t += 1.0
        cell.step_phase(t, amplitude_mv, period_hours)
        if t >= (settle_min + next_sample) - 1e-9:
            # The reader sees the cell's voltage plus imaging/measurement
            # noise, and a reference trace it measures separately (an
            # unexposed region, or the media potassium level).
            v_samples.append(cell.V + rng.normal(0, measurement_noise_std))
            r_samples.append(ambient_oscillation_offset(t, amplitude_mv, period_hours))
            next_sample += SAMPLE_EVERY_MIN

    return int(phase_read(v_samples, r_samples) == bit)


def run_level_trial(bit: int, amplitude_mv: float, period_hours: float,
                    seed: int, window_min: float, measurement_noise_std: float,
                    settle_min: float = 60.0,
                    params: GardnerParams = None,
                    tx_noise: float = 3.0) -> int:
    """This project's EXISTING level-encoding scheme, reproduced here under
    identical conditions so the comparison is fair: static V_HIGH/V_LOW
    target, ambient oscillation added to the voltage (the treatment
    bsubtilis_08_native_oscillation_interference.py established), read by averaging the
    thresholded samples over the same window."""
    params = params or GardnerParams()
    cell = GardnerToggleCell(params, seed=seed, transcriptional_noise_std=tx_noise)
    cell.write(bit)
    rng = np.random.default_rng(seed + 7919)

    t = 0.0
    for _ in range(int(settle_min)):
        t += 1.0
        cell.step(dt=0.02)
        cell.V = float(np.clip(
            cell.V + ambient_oscillation_offset(t, amplitude_mv, period_hours), -120, 60))

    reads = []
    next_sample = SAMPLE_EVERY_MIN
    for _ in range(int(window_min)):
        t += 1.0
        cell.step(dt=0.02)
        cell.V = float(np.clip(
            cell.V + ambient_oscillation_offset(t, amplitude_mv, period_hours), -120, 60))
        if t >= (settle_min + next_sample) - 1e-9:
            measured = cell.V + rng.normal(0, measurement_noise_std)
            reads.append(1 if measured > cell.V_MID else 0)
            next_sample += SAMPLE_EVERY_MIN

    if not reads:
        return 0
    return int((1 if np.mean(reads) > 0.5 else 0) == bit)


def accuracy(scheme: str, amplitude_mv: float, window_min: float,
             measurement_noise_std: float, n_trials: int = 12,
             period_hours: float = DEFAULT_PERIOD_H,
             response_fraction: float = 1.0,
             n_start_phases: int = 6) -> float:
    """Average accuracy across trials AND across several read start times
    spread evenly over one full oscillation period.

    The start-phase sweep is not a detail. A read that always begins at the
    same point in the cycle is accidentally phase-locked, which flatters
    level encoding for the wrong reason (it is a free version of the timing
    trick bsubtilis_11_phase_locked_readout.py already ruled out). A real reader does not
    know where in the cycle it is arriving. This matches how
    bsubtilis_09_eis_readout_interference.py spreads its readout times across the day."""
    runner = run_phase_trial if scheme == "phase" else run_level_trial
    period_min = period_hours * 60.0
    starts = [60.0 + i * period_min / n_start_phases for i in range(n_start_phases)]

    correct, total = 0, 0
    for bit in [0, 1]:
        for trial in range(n_trials):
            for start in starts:
                seed = int(amplitude_mv * 131) + trial * 37 + bit * 11 + int(start)
                kwargs = dict(period_hours=period_hours, seed=seed,
                              window_min=window_min, settle_min=start,
                              measurement_noise_std=measurement_noise_std)
                if scheme == "phase":
                    kwargs["response_fraction"] = response_fraction
                correct += runner(bit, amplitude_mv, **kwargs)
                total += 1
    return correct / total


def main():
    print("=" * 78)
    print("PHASE-ENCODED READOUT - the native oscillation as carrier, not noise")
    print("Tests the framing from Yang et al. 2020, Cell Systems,")
    print("DOI 10.1016/j.cels.2020.04.002, against this project's own level encoding.")
    print("SENSITIVITY ANALYSIS UNDER AN ASSUMED COUPLING, NOT A PREDICTION (audit Part 26).")
    print("=" * 78)

    amplitudes = [0.0, 10.0, 30.0, 50.0, 70.0]

    print("\n--- Table 1: the predicted inversion ---")
    print("60-minute read, moderate measurement noise (10mV-equivalent)")
    print(f"{'Ambient amplitude (mV)':<26}{'Level encoding':>18}{'Phase encoding':>18}")
    for amp in amplitudes:
        lvl = accuracy("level", amp, 60, 10.0)
        pha = accuracy("phase", amp, 60, 10.0)
        print(f"{amp:<26.0f}{lvl:>17.0%}{pha:>18.0%}")

    print("\n--- Table 2: where phase encoding breaks (measurement noise sweep) ---")
    print("60-minute read. Measurement noise has no citation, so it is swept.")
    noises = [0.0, 5.0, 10.0, 20.0, 40.0]
    header = f"{'Meas. noise (mV)':<20}" + "".join(f"{a:>11.0f}mV" for a in amplitudes[1:])
    print(header)
    for noise in noises:
        row = f"{noise:<20.0f}"
        for amp in amplitudes[1:]:
            row += f"{accuracy('phase', amp, 60, noise):>12.0%}"
        print(row)

    print("\n--- Table 3: how long a read phase encoding needs ---")
    print("Moderate measurement noise (10mV-equivalent), 3h ambient period")
    windows = [10, 30, 60, 120, 180]
    header = f"{'Window (min)':<20}" + "".join(f"{a:>11.0f}mV" for a in amplitudes[1:])
    print(header)
    for win in windows:
        row = f"{win:<20d}"
        for amp in amplitudes[1:]:
            row += f"{accuracy('phase', amp, win, 10.0):>12.0%}"
        print(row)

    print("\n--- Table 4: partial coupling (a weaker phase response) ---")
    print("60-minute read, 10mV measurement noise. response_fraction is")
    print("how much of the ambient swing the cell reproduces. Unmeasured.")
    header = f"{'response_fraction':<20}" + "".join(f"{a:>11.0f}mV" for a in amplitudes[1:])
    print(header)
    for frac in [1.0, 0.5, 0.25, 0.1]:
        row = f"{frac:<20.2f}"
        for amp in amplitudes[1:]:
            row += f"{accuracy('phase', amp, 60, 10.0, response_fraction=frac):>12.0%}"
        print(row)

    print("\n" + "=" * 78)
    print("WHAT THIS RUN FOUND")
    print("=" * 78)
    print("The predicted inversion holds. Level encoding is perfect with no")
    print("oscillation and collapses to near chance (54-65%) once the ambient")
    print("swing is present, reproducing bsubtilis_08_native_oscillation_interference.py's")
    print("own 50-59% result and confirming the two files agree. Phase encoding")
    print("does the opposite: it fails at exactly chance (50%) with no carrier,")
    print("which is the control working as it should, and climbs to 99-100% at")
    print("30mV and above. The oscillation that breaks one scheme is what makes")
    print("the other one work.")
    print()
    print("What phase encoding costs, from Tables 2-4: a read of roughly 60")
    print("minutes or more (a 10-minute read is near chance), measurement noise")
    print("held under about 20mV-equivalent at the low end of the amplitude")
    print("range, and a strong coupling between the stored bit and the cell's")
    print("potassium response (at 10% coupling it degrades to 49-76%).")
    print("None of those three numbers has been measured, here or in the source")
    print("paper, for a genetically driven version of this mechanism.")
    print()
    print("A DIRECT CONFLICT THIS CREATES WITH AUDIT PART 18:")
    print("bsubtilis_12_decoupled_channel_readout.py recommends weakening or deleting yugO to")
    print("reduce the native signal reaching the circuit. Yang et al. 2020 show a")
    print("delta-yugO strain does not respond to the write stimulus at all. So")
    print("for level encoding yugO is the problem, and for phase encoding yugO is")
    print("the mechanism. The two strategies are mutually exclusive and the")
    print("project has to pick one before choosing a chassis strain.")
    print()
    print("REMEMBER WHAT IS UNBUILT: Yang et al. wrote their bit with light")
    print("onto native yugO channels, not with a genetic circuit. The link")
    print("from a toggle switch's state to a cell's in-phase or anti-phase")
    print("potassium behavior is unbuilt and unmeasured, the same status as")
    print("the repressor-to-ion-channel link in bsubtilis_01_gardner_toggle_circuit.py.")
    print("Not tested here: whether a phase-encoded bit survives damage and")
    print("regrowth the way the genetic state does (Parts 8, 20, 22).")


if __name__ == "__main__":
    main()
