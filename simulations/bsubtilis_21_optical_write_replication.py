"""
Acheron Simulation 25: Reimplementing the Yang et al. 2020 Optical Write, and
Running the One Test They Did Not Run
================================================================================

WHY THIS FILE EXISTS:
The founder asked whether the UC San Diego work on writing memory into
B. subtilis membrane potential can be used as the basis for a simulation of
the WRITE step in this project's own chosen organism. This file is the
answer, and the answer has two halves: what can be reused, and what cannot.

WHAT CANNOT BE REUSED, STATED FIRST:
Yang et al.'s own "Data and Code Availability" statement says, verbatim,
"This study did not generate new code nor software. All raw data are
available upon request from the Lead Contact." So there is no deposited
dataset and no released code to run. Their model's parameter table is in
supplementary Table S1, which is not in the open-access full text this
project has access to. Nothing in this file is fitted to their raw data,
because their raw data is not public.

WHAT CAN BE REUSED:
The structure of their model is described in full prose in the paper's STAR
Methods, and the observables they report are in the main text. That is
enough to reimplement the mechanism and then check the reimplementation
against their reported results. That is what this file does.

THE PAPER:
Yang, Bialecka-Fornal, Weatherwax, Larkin, Prindle, Liu, Garcia-Ojalvo &
Suel (2020), "Encoding membrane potential-based memory within a microbial
community," Cell Systems 10(5):417-423, DOI 10.1016/j.cels.2020.04.002,
PMID 32343961, PMC7286314. B. subtilis NCIB 3610, yugO potassium channel,
Thioflavin T at 10 uM as the membrane potential reporter. Retrieved via
PubMed Central.

THE MODEL, AS THEIR STAR METHODS DESCRIBES IT:
  - Membrane potential depends on potassium current through the channels
    plus a generic leak current (a Hodgkin-Huxley form, following their own
    earlier Prindle et al. 2015 and Martinez-Corral et al. models).
  - The leak reversal potential is a linear function that increases with
    extracellular potassium.
  - The potassium reversal potential is the Nernst potential.
  - Local extracellular and intracellular potassium are both state
    variables. Potassium moves through the channels or is actively pumped,
    and local extracellular potassium relaxes toward the global level of
    the medium.
  - The channel has four subunits; n is the fraction in the open state.
  - Channel opening rate depends on metabolic stress, and stress is
    triggered by changes in membrane potential.
  - ThT signal depends on the difference between a fixed voltage and the
    membrane potential, and decays.
  - THE WRITE: "we assume that irradiation fixes the subunits of the
    potassium channels," i.e. n is clamped at a constant for exposed cells.

PARAMETER PROVENANCE, PER THE NO-NUMERIC-INVENTION RULE:
  - RT/F = 26.7 mV is the physical constant at 30 C, which is the
    temperature their protocol runs at after the first 90 minutes.
  - 8 mM and 150 mM external potassium, the 100 minute alternation period,
    the 50 minute expected cross-correlation lag, the 5 second exposure and
    the 3 hour persistence window are all taken from the paper's main text.
  - Intracellular potassium of 300 mM is the standard textbook range for
    bacteria, not a number from this paper.
  - Every other constant below is a STRUCTURAL PLACEHOLDER chosen so the
    model sits in a physiologically ordinary resting range. They are NOT
    Yang et al.'s values, they are not fitted to any measurement, and no
    result in this file should be quoted as a measured quantity. They are
    labelled UNCALIBRATED in the code.

WHAT THIS FILE THEN DOES THAT THE PAPER DOES NOT:
Their memory is a protein-level modification of existing channels. Their
own Discussion says it "does not arise from positive feedback, but rather
from enduring modifications at the protein level," and notes that biofilm
cells are "predominantly non-replicating," which is part of why the pattern
lasts at all. Acheron's entire premise is data surviving damage and
REGROWTH, which means division. So this file runs the optical write forward
through cell division, against a genetic latch of the kind
bsubtilis_01_gardner_toggle_circuit.py models, and compares.

That comparison is the part that does not depend on the uncalibrated
constants: a protein mark laid down once is diluted by a factor of two per
generation as unmodified channels are synthesised, whatever the rate
constants are, while a latch that re-establishes the state each generation
is not. The dilution result is arithmetic on the mechanism, not a fit.

SEE ALSO:
  - docs/SCIENTIFIC_AUDIT_2026.md Part 25 for what this paper does and does
    not take away from this project's novelty claim.
  - simulations/bsubtilis_18_phase_encoded_readout.py, which tests phase
    encoding phenomenologically with an imposed sinusoid rather than
    deriving it from the potassium mechanism as this file does.
  - simulations/bsubtilis_07_colony_regrowth.py for the genetic side of the
    comparison run here.
"""

import math
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Constants taken from the paper's main text or from physics.
# ---------------------------------------------------------------------------

RT_OVER_F_MV = 26.7          # mV at 30 C, the paper's experimental temperature
K_EXT_NORMAL_MM = 8.0        # paper: "regular (8 mM K)" medium
K_EXT_SHOCK_MM = 150.0       # paper: "high (150 mM K)"
SHOCK_PERIOD_MIN = 100.0     # paper: pre-determined alternation period
EXPECTED_LAG_MIN = 50.0      # paper: max cross-correlation at half the period
PERSISTENCE_WINDOW_MIN = 200.0   # paper observed "over 3 hours"

# ---------------------------------------------------------------------------
# UNCALIBRATED structural placeholders. Not from the paper. See header.
# ---------------------------------------------------------------------------

K_INT_SETPOINT_MM = 300.0    # textbook bacterial intracellular potassium
G_K = 0.30                   # channel conductance, per minute
G_L = 0.10                   # leak conductance, per minute
V_LEAK_BASE_MV = -82.0       # leak reversal at zero external potassium
V_LEAK_SLOPE = 0.15          # mV per mM, paper says leak reversal rises with K_e
FLUX_EXT = 0.020             # how much channel current moves local external K
FLUX_INT = 0.020             # how much channel current moves internal K
RELAX_EXT = 0.10             # local external K relaxes to the global level
PUMP_INT = 0.05              # active pumping of internal K back to setpoint
STRESS_GAIN = 0.60           # stress produced per mV of depolarisation
STRESS_TAU_MIN = 8.0         # stress relaxation time
OPEN_RATE = 0.25             # channel opening rate at full stress
CLOSE_RATE = 0.08            # channel closing rate
STRESS_HALF = 4.0            # half-saturating stress for channel opening
N_REST = 0.10                # resting open fraction of unexposed cells
N_LIGHT = 0.80               # open fraction the light clamp leaves behind
THT_VOLTAGE_MV = 0.0         # the "fixed voltage" in the paper's ThT equation
THT_GAIN = 0.05
THT_DECAY = 0.04
DT_MIN = 0.05                # integration step, minutes


def nernst_potassium(k_ext_mm: float, k_int_mm: float) -> float:
    """Potassium reversal potential, in mV."""
    return RT_OVER_F_MV * math.log(max(k_ext_mm, 1e-6) / max(k_int_mm, 1e-6))


def leak_reversal(k_ext_mm: float) -> float:
    """Leak reversal potential. The paper states this rises linearly with
    extracellular potassium; the two constants are uncalibrated."""
    return V_LEAK_BASE_MV + V_LEAK_SLOPE * k_ext_mm


class KChannelCell:
    """One B. subtilis cell in the Yang et al. framework.

    `clamped_n` is the optical write. When it is not None the open fraction
    is held at that value, which is exactly the paper's statement that
    "irradiation fixes the subunits of the potassium channels."

    `channel_gain` is the yugO knockout control: 0.0 is the delta-yugO
    strain, which the paper uses as its key genetic control.
    """

    def __init__(self, clamped_n: float = None, channel_gain: float = 1.0):
        self.clamped_n = clamped_n
        self.channel_gain = channel_gain
        self.k_ext = K_EXT_NORMAL_MM
        self.k_int = K_INT_SETPOINT_MM
        self.n = N_REST if clamped_n is None else clamped_n
        self.stress = 0.0
        self.v = leak_reversal(K_EXT_NORMAL_MM)
        self.tht = 0.0
        self._v_reference = self.v

    def step(self, k_global_mm: float, dt: float = DT_MIN) -> None:
        v_k = nernst_potassium(self.k_ext, self.k_int)
        v_l = leak_reversal(self.k_ext)

        open_fraction = self.n ** 4
        i_k = self.channel_gain * G_K * open_fraction * (self.v - v_k)
        i_l = G_L * (self.v - v_l)

        self.v += dt * (-(i_k + i_l))

        # Potassium bookkeeping. Outward current removes internal potassium
        # and adds to the local external pool, which relaxes to the medium.
        self.k_ext += dt * (FLUX_EXT * i_k - RELAX_EXT * (self.k_ext - k_global_mm))
        self.k_int += dt * (-FLUX_INT * i_k - PUMP_INT * (self.k_int - K_INT_SETPOINT_MM))
        self.k_ext = max(self.k_ext, 0.1)
        self.k_int = max(self.k_int, 1.0)

        # Stress rises with depolarisation away from the cell's own reference
        # potential, and gates channel opening. Paper: "the rate of opening of
        # the channels is assumed to depend on metabolic stress... Stress is
        # triggered by changes in membrane potential."
        drive = max(0.0, self.v - self._v_reference) * STRESS_GAIN
        self.stress += dt * ((drive - self.stress) / STRESS_TAU_MIN)

        if self.clamped_n is None:
            gate = self.stress / (self.stress + STRESS_HALF)
            self.n += dt * (OPEN_RATE * gate * (1.0 - self.n) - CLOSE_RATE * self.n)
            self.n = min(max(self.n, 0.0), 1.0)
        else:
            self.n = self.clamped_n

        # ThT reporter, per the paper's own form.
        self.tht += dt * (THT_GAIN * (THT_VOLTAGE_MV - self.v) - THT_DECAY * self.tht)


def settle(cell: KChannelCell, minutes: float, k_global_mm: float) -> None:
    for _ in range(int(minutes / DT_MIN)):
        cell.step(k_global_mm)


def trace(cell: KChannelCell, minutes: float, k_global_fn) -> Tuple[List[float], List[float], List[float]]:
    """Run a cell and return (time_min, voltage_mv, tht)."""
    times, volts, thts = [], [], []
    steps = int(minutes / DT_MIN)
    for i in range(steps):
        t = i * DT_MIN
        cell.step(k_global_fn(t))
        times.append(t)
        volts.append(cell.v)
        thts.append(cell.tht)
    return times, volts, thts


# ---------------------------------------------------------------------------
# Signature checks against what the paper actually reports.
# ---------------------------------------------------------------------------

def signature_1_light_hyperpolarises() -> Dict:
    """Paper: a 5 s blue light exposure hyperpolarises exposed cells, seen as
    an increase in ThT intensity, measured 40 minutes after exposure."""
    unexposed = KChannelCell()
    settle(unexposed, 120.0, K_EXT_NORMAL_MM)
    baseline_v = unexposed.v

    exposed = KChannelCell()
    settle(exposed, 120.0, K_EXT_NORMAL_MM)
    exposed.clamped_n = N_LIGHT          # the write
    settle(exposed, 40.0, K_EXT_NORMAL_MM)
    settle(unexposed, 40.0, K_EXT_NORMAL_MM)

    return {
        "baseline_mv": baseline_v,
        "unexposed_mv": unexposed.v,
        "exposed_mv": exposed.v,
        "shift_mv": exposed.v - unexposed.v,
        "hyperpolarised": exposed.v < unexposed.v,
    }


def signature_2_yugo_knockout_is_deaf() -> Dict:
    """Paper: the delta-yugO deletion strain shows no noticeable membrane
    potential change on light exposure."""
    wt = KChannelCell()
    settle(wt, 120.0, K_EXT_NORMAL_MM)
    wt_before = wt.v
    wt.clamped_n = N_LIGHT
    settle(wt, 40.0, K_EXT_NORMAL_MM)

    ko = KChannelCell(channel_gain=0.0)
    settle(ko, 120.0, K_EXT_NORMAL_MM)
    ko_before = ko.v
    ko.clamped_n = N_LIGHT
    settle(ko, 40.0, K_EXT_NORMAL_MM)

    return {
        "wt_shift_mv": wt.v - wt_before,
        "knockout_shift_mv": ko.v - ko_before,
        "knockout_is_deaf": abs(ko.v - ko_before) < 0.1 * abs(wt.v - wt_before),
    }


def signature_3_excess_potassium_blocks_the_write() -> Dict:
    """Paper: excess extracellular potassium prevents the hyperpolarisation;
    excess sodium does not. Sodium is not in this model at all, which is
    itself the point: a potassium-only model cannot produce a sodium effect,
    so only the potassium half of this control is testable here."""
    normal = KChannelCell()
    settle(normal, 120.0, K_EXT_NORMAL_MM)
    normal_before = normal.v
    normal.clamped_n = N_LIGHT
    settle(normal, 40.0, K_EXT_NORMAL_MM)

    clamped = KChannelCell()
    settle(clamped, 120.0, K_EXT_SHOCK_MM)
    clamped_before = clamped.v
    clamped.clamped_n = N_LIGHT
    settle(clamped, 40.0, K_EXT_SHOCK_MM)

    return {
        "normal_shift_mv": normal.v - normal_before,
        "excess_k_shift_mv": clamped.v - clamped_before,
        "blocked": (clamped.v - clamped_before) > (normal.v - normal_before),
    }


def signature_4_pattern_persists() -> Dict:
    """Paper: ThT intensity reached its maximum within minutes and remained at
    a steady state throughout an observation of over 3 hours."""
    exposed = KChannelCell()
    unexposed = KChannelCell()
    settle(exposed, 120.0, K_EXT_NORMAL_MM)
    settle(unexposed, 120.0, K_EXT_NORMAL_MM)
    exposed.clamped_n = N_LIGHT

    separations = []
    checkpoints = [5.0, 30.0, 60.0, 120.0, PERSISTENCE_WINDOW_MIN]
    elapsed = 0.0
    for mark in checkpoints:
        step_minutes = mark - elapsed
        settle(exposed, step_minutes, K_EXT_NORMAL_MM)
        settle(unexposed, step_minutes, K_EXT_NORMAL_MM)
        elapsed = mark
        separations.append((mark, exposed.v - unexposed.v))

    early = separations[0][1]
    late = separations[-1][1]
    return {
        "separations_mv": separations,
        "holds_steady": abs(late) > 0.8 * abs(early) if early != 0 else False,
    }


def _cross_correlation_lag(a: List[float], b: List[float], max_lag_steps: int) -> Tuple[float, float]:
    """Return (lag at maximum correlation in steps, correlation at zero lag)."""
    def centred(xs):
        m = sum(xs) / len(xs)
        return [x - m for x in xs]

    ac, bc = centred(a), centred(b)

    def corr(lag: int) -> float:
        if lag >= len(ac):
            return 0.0
        x = ac[lag:]
        y = bc[: len(ac) - lag]
        num = sum(p * q for p, q in zip(x, y))
        da = math.sqrt(sum(p * p for p in x))
        db = math.sqrt(sum(q * q for q in y))
        return num / (da * db) if da > 0 and db > 0 else 0.0

    best_lag, best_val = 0, -2.0
    for lag in range(max_lag_steps):
        c = corr(lag)
        if c > best_val:
            best_lag, best_val = lag, c
    return best_lag, corr(0)


def _shock_schedule(t: float) -> float:
    half = SHOCK_PERIOD_MIN / 2.0
    return K_EXT_SHOCK_MM if (t % SHOCK_PERIOD_MIN) < half else K_EXT_NORMAL_MM


def antiphase_trial(flux_int: float, pump_int: float, g_k: float) -> Dict:
    """Run the potassium-shock experiment with three of the uncalibrated
    constants overridden. Used by the sweep below; the module defaults are
    not modified."""
    global FLUX_INT, PUMP_INT, G_K
    saved = (FLUX_INT, PUMP_INT, G_K)
    FLUX_INT, PUMP_INT, G_K = flux_int, pump_int, g_k
    try:
        return signature_5_antiphase_under_potassium_shock()
    finally:
        FLUX_INT, PUMP_INT, G_K = saved


def antiphase_parameter_sweep() -> List[Dict]:
    """Ask whether the paper's signature 5 is reachable at all in this model
    structure, rather than concluding from one parameter choice that it is not.

    The three constants swept are the ones that decide whether INTRACELLULAR
    potassium is free to move: how strongly channel current shifts it, how
    hard it is pumped back, and how much current the channels can carry. That is the hinge: the paper's explanation
    requires unexposed cells to hyperpolarise under excess external potassium,
    which in a Nernst model needs internal potassium to rise enough to keep
    the reversal potential below the membrane potential. If internal potassium
    is pinned to a setpoint by strong pumping, channel opening can only
    depolarise, and anti-phase cannot appear at any other setting.

    This is a sweep, not a calibration. A region that reproduces their
    signature would tell us what their Table S1 has to look like; it would
    not tell us that it does look like that.
    """
    rows = []
    for flux_int in (0.02, 0.30, 2.00):
        for pump_int in (0.0005, 0.05):
            for g_k in (0.30, 3.00):
                result = antiphase_trial(flux_int, pump_int, g_k)
                rows.append({
                    "flux_int": flux_int,
                    "pump_int": pump_int,
                    "g_k": g_k,
                    "zero_lag": result["zero_lag_correlation"],
                    "peak_lag_min": result["peak_lag_min"],
                    "antiphase": result["antiphase_at_zero_lag"],
                    "lag_matches": result["peak_lag_matches"],
                })
    return rows


def signature_5_antiphase_under_potassium_shock() -> Dict:
    """Paper: under alternating 150 mM and 8 mM external potassium with a 100
    minute period, exposed and unexposed regions are anti-correlated at zero
    lag and maximally correlated at 50 minutes lag.

    This is the signature that most depends on the parameters in their
    Table S1, because it comes from the ACTIVE gating of unexposed cells,
    not from the passive clamp of exposed ones. The result is reported as
    it comes out rather than tuned to match.
    """
    k_global = _shock_schedule

    exposed = KChannelCell()
    unexposed = KChannelCell()
    settle(exposed, 120.0, K_EXT_NORMAL_MM)
    settle(unexposed, 120.0, K_EXT_NORMAL_MM)
    exposed.clamped_n = N_LIGHT
    settle(exposed, 40.0, K_EXT_NORMAL_MM)
    settle(unexposed, 40.0, K_EXT_NORMAL_MM)

    duration = SHOCK_PERIOD_MIN * 4
    _, ve, _ = trace(exposed, duration, k_global)
    _, vu, _ = trace(unexposed, duration, k_global)

    # Downsample to the paper's own 5 minute imaging interval.
    stride = int(5.0 / DT_MIN)
    ve_s = ve[::stride]
    vu_s = vu[::stride]

    max_lag_steps = int(SHOCK_PERIOD_MIN / 5.0)
    lag_steps, zero_lag = _cross_correlation_lag(ve_s, vu_s, max_lag_steps)
    lag_min = lag_steps * 5.0

    return {
        "zero_lag_correlation": zero_lag,
        "peak_lag_min": lag_min,
        "expected_peak_lag_min": EXPECTED_LAG_MIN,
        "antiphase_at_zero_lag": zero_lag < 0.0,
        "peak_lag_matches": abs(lag_min - EXPECTED_LAG_MIN) <= 10.0,
    }


# ---------------------------------------------------------------------------
# The test the paper does not run: what division does to each kind of write.
# ---------------------------------------------------------------------------

def division_comparison(generations: int = 8) -> List[Dict]:
    """Compare an optical (protein-level) write against a genetic latch
    across cell generations.

    The optical write is a fixed population of modified channel subunits.
    Every generation the cell doubles its channel pool with newly
    synthesised, unmodified channels, so the modified FRACTION halves. This
    is arithmetic on the mechanism the paper itself describes, and it does
    not depend on any rate constant in this file.

    The genetic latch re-establishes the open fraction in every daughter
    cell from the inherited toggle state, so it does not dilute. That
    inheritance is the assumption bsubtilis_07_colony_regrowth.py tests
    separately, and it is an assumption, not a measurement.
    """
    baseline = KChannelCell()
    settle(baseline, 120.0, K_EXT_NORMAL_MM)
    resting_v = baseline.v

    rows = []
    for g in range(generations + 1):
        optical_n = N_REST + (N_LIGHT - N_REST) * (0.5 ** g)
        genetic_n = N_LIGHT

        optical_cell = KChannelCell(clamped_n=optical_n)
        settle(optical_cell, 60.0, K_EXT_NORMAL_MM)
        genetic_cell = KChannelCell(clamped_n=genetic_n)
        settle(genetic_cell, 60.0, K_EXT_NORMAL_MM)

        rows.append({
            "generation": g,
            "optical_open_fraction": optical_n,
            "optical_separation_mv": optical_cell.v - resting_v,
            "genetic_separation_mv": genetic_cell.v - resting_v,
        })
    return rows


def readable_generations(rows: List[Dict], threshold_mv: float) -> int:
    """How many generations the optical write stays above a given readout
    threshold. The threshold is a free parameter because no one has measured
    the real ThT discrimination limit in this setting."""
    count = 0
    for row in rows:
        if abs(row["optical_separation_mv"]) >= threshold_mv:
            count = row["generation"]
        else:
            break
    return count


def main() -> None:
    print("=" * 78)
    print("ACHERON SIMULATION 25: Yang et al. 2020 optical write, reimplemented")
    print("=" * 78)
    print()
    print("Source: Yang et al. (2020) Cell Systems 10(5):417-423,")
    print("DOI 10.1016/j.cels.2020.04.002, PMID 32343961, via PubMed Central.")
    print("Their raw data is request-only and they released no code, so this is")
    print("a reimplementation of the described mechanism, not a re-analysis of")
    print("their measurements. Rate constants here are UNCALIBRATED placeholders.")
    print()

    print("-" * 78)
    print("PART 1. Does the reimplementation reproduce what they report?")
    print("-" * 78)
    print()

    s1 = signature_1_light_hyperpolarises()
    print("Signature 1, light hyperpolarises exposed cells")
    print(f"  unexposed  {s1['unexposed_mv']:8.2f} mV")
    print(f"  exposed    {s1['exposed_mv']:8.2f} mV")
    print(f"  shift      {s1['shift_mv']:8.2f} mV")
    print(f"  REPRODUCED: {s1['hyperpolarised']}")
    print()

    s2 = signature_2_yugo_knockout_is_deaf()
    print("Signature 2, the delta-yugO knockout does not respond to light")
    print(f"  wild type shift  {s2['wt_shift_mv']:8.2f} mV")
    print(f"  knockout shift   {s2['knockout_shift_mv']:8.2f} mV")
    print(f"  REPRODUCED: {s2['knockout_is_deaf']}")
    print()

    s3 = signature_3_excess_potassium_blocks_the_write()
    print("Signature 3, excess extracellular potassium blocks the write")
    print(f"  shift in 8 mM    {s3['normal_shift_mv']:8.2f} mV")
    print(f"  shift in 150 mM  {s3['excess_k_shift_mv']:8.2f} mV")
    print(f"  REPRODUCED: {s3['blocked']}")
    print("  (the sodium half of their control cannot be tested in a")
    print("   potassium-only model, so it is not claimed here)")
    print()

    s4 = signature_4_pattern_persists()
    print("Signature 4, the written pattern holds for hours")
    for mark, sep in s4["separations_mv"]:
        print(f"  t = {mark:6.1f} min   separation {sep:7.2f} mV")
    print(f"  REPRODUCED: {s4['holds_steady']}")
    print()

    s5 = signature_5_antiphase_under_potassium_shock()
    print("Signature 5, anti-phase response under a 100 minute potassium cycle")
    print(f"  correlation at zero lag   {s5['zero_lag_correlation']:7.3f}")
    print(f"  lag of peak correlation   {s5['peak_lag_min']:7.1f} min")
    print(f"  paper reports             {s5['expected_peak_lag_min']:7.1f} min")
    print(f"  anti-correlated at zero lag: {s5['antiphase_at_zero_lag']}")
    print(f"  peak lag within 10 min of theirs: {s5['peak_lag_matches']}")
    print()
    print("  Signature 5 does not come out of the default constants. Rather than")
    print("  leave that as one failed run, sweep the two constants that decide")
    print("  whether internal potassium is free to move, which is the hinge the")
    print("  paper's own explanation turns on.")
    print()
    sweep = antiphase_parameter_sweep()
    print(f"  {'K influx':>9}  {'K pumping':>10}  {'g_K':>6}  {'zero lag':>9}  {'peak lag':>9}  {'anti-phase':>11}")
    for row in sweep:
        print(f"  {row['flux_int']:>9.3f}  {row['pump_int']:>10.4f}  {row['g_k']:>6.2f}"
              f"  {row['zero_lag']:>9.3f}  {row['peak_lag_min']:>7.1f}m"
              f"  {str(row['antiphase']):>11}")
    hits = [r for r in sweep if r["antiphase"]]
    matches = [r for r in sweep if r["antiphase"] and r["lag_matches"]]
    print()
    print(f"  anti-phase reached in {len(hits)} of {len(sweep)} settings,"
          f" and with their 50 minute lag in {len(matches)}")
    if not hits:
        print("  So signature 5 is NOT reachable anywhere in this sweep. That is a")
        print("  gap in the reimplementation, not a challenge to their result:")
        print("  they report it experimentally, with microfluidics, not only in")
        print("  simulation. The missing piece is their Table S1.")
    else:
        print("  So the mechanism can produce their signature, in the corner of the")
        print("  space where internal potassium is free to move. That is a")
        print("  prediction about what their Table S1 must contain, nothing more.")
    print()

    print("-" * 78)
    print("PART 2. The test they did not run: cell division")
    print("-" * 78)
    print()
    print("Their memory is a protein modification of existing channels, and")
    print("their Discussion notes biofilm cells are predominantly non-")
    print("replicating. Acheron needs the bit to survive REGROWTH, which means")
    print("division. Each generation halves the modified channel fraction.")
    print()
    rows = division_comparison(generations=8)
    print(f"  {'gen':>4}  {'open frac':>10}  {'optical (mV)':>14}  {'genetic (mV)':>14}")
    for row in rows:
        print(f"  {row['generation']:>4}  {row['optical_open_fraction']:>10.4f}"
              f"  {row['optical_separation_mv']:>14.2f}"
              f"  {row['genetic_separation_mv']:>14.2f}")
    print()
    for threshold in (5.0, 2.0, 1.0):
        gens = readable_generations(rows, threshold)
        print(f"  at a {threshold:.0f} mV readout threshold, the optical write"
              f" is readable for {gens} generations")
    print()
    print("  B. subtilis doubles in roughly 30 minutes in rich media, so those")
    print("  generation counts are hours, not days. The genetic column does not")
    print("  fall, by construction: it assumes the latch is inherited, which is")
    print("  exactly the assumption the wet lab has to test and nobody has.")
    print()

    print("-" * 78)
    print("WHAT THIS DOES AND DOES NOT SHOW")
    print("-" * 78)
    print()
    print("Shows: the write step has a published physical mechanism in this")
    print("  project's own target organism, and that mechanism can be")
    print("  reimplemented from the paper's prose without their data.")
    print("Does not show: that the numbers above are quantitatively right.")
    print("  The rate constants are uncalibrated. Their Table S1 is not in the")
    print("  open-access text, and their raw data is available only by request")
    print("  to the Lead Contact, Gurol Suel at UC San Diego.")
    print("Does not show: that a genetic latch can drive channel state at all.")
    print("  That link is unbuilt and unmeasured, the same status it has in")
    print("  bsubtilis_01_gardner_toggle_circuit.py.")
    print()


if __name__ == "__main__":
    main()
