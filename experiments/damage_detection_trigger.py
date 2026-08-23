"""
Acheron Experiment: Damage-Detection Trigger — Is the Wound Signal
Detectable Fast Enough to Justify the Current Polling Assumption?
=============================================================================

WHY THIS EXISTS:
Handoff fidelity, imperfect healing, and field-mediated persistence have
all now been touched by simulation -- but the very first step in "detect
damage -> handoff -> heal -> return" has not: how does the system know it
needs to heal at all? regeneration_data_loss_window.py currently ASSUMES
detection latency is Normal(30min, 10min), modeling a fixed polling
schedule ("silicon polls voltage imaging every 30 min"), not an actual
signal-vs-noise detection process. This script tests whether that
assumption is consistent with the real biology of the signal it would be
trying to detect.

REAL DATA THIS IS GROUNDED IN:
"The Role of Early Bioelectric Signals in the Regeneration of Planarian
Anterior/Posterior Polarity," Biophysical Journal (2019), PMID 30799071.
Wound-site depolarization is detectable within ~1 hour post-injury and
causally determines regeneration outcome by ~3 hours -- real, cited
timing, used below to shape the signal's rise. The paper does not report
a millivolt magnitude in directly reusable form, so magnitude is SWEPT as
an explicit parameter rather than asserted -- see WHAT THIS DOES NOT DO.

MODEL:
A sentinel voltage readout at the wound site rises from baseline toward
an assumed asymptotic depolarization, following a time course calibrated
so it reaches ~95% of that asymptote by 3h (matching the causal-
determination milestone above). This is superimposed on Acheron's own
"Realistic biological noise" profile -- the SAME channel/thermal noise
parameters used throughout noise_floor_characterizer.py and
biofilm_tile_handoff.py, not new ones. Detection is modeled as a
threshold crossing on a smoothed readout, with the threshold set from a
target false-positive rate on the noise statistics themselves -- so
detection latency here is a CONSEQUENCE of signal and noise, not an
assumed polling interval.

WHAT THIS DOES NOT DO:
The wound-depolarization MAGNITUDE is not reported in the cited paper in
directly reusable form, so it is swept here across a range (10-100% of
the ~70mV V_HIGH/V_LOW range already used elsewhere in this repo) rather
than asserted as one number. Only the TIMING (rise reaching ~95% by 3h)
and the NOISE parameters (reused, not new) are grounded in existing
citable sources. This does not model WHERE the sentinel readout comes
from physically (how many cells, what imaging modality) -- it assumes a
single scalar readout with the stated noise level, which is optimistic
if real imaging would need to average over fewer cells than assumed.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ANALYSIS_DIR = Path(__file__).resolve().parents[1] / "analysis"

# Acheron's own "Realistic biological noise" profile
# (simulations/noise_floor_characterizer.py, biofilm_tile_handoff.py's
# TileNoise defaults) -- reused here, not redefined.
CHANNEL_NOISE_STD_MV = 5.0
THERMAL_NOISE_STD_MV = 0.4

# Current assumption in regeneration_data_loss_window.py, for comparison.
CURRENT_ASSUMPTION_MEAN_H = 0.5
CURRENT_ASSUMPTION_STD_H = 0.17
CURRENT_ASSUMPTION_MIN_H = 0.08

RISE_TAU_H = 1.0  # calibrated so signal(3h) ~= 95% of asymptote, per PMID 30799071's 3h milestone


def signal(t_h: np.ndarray, magnitude_mv: float) -> np.ndarray:
    return magnitude_mv * (1.0 - np.exp(-t_h / RISE_TAU_H))


def false_positive_threshold(smoothing_window: int, target_fpr: float) -> float:
    """Threshold (mV) on a `smoothing_window`-sample moving-average readout
    that gives a one-sided false-positive rate of `target_fpr` per sample,
    under baseline (no-signal) noise alone."""
    from scipy.stats import norm

    effective_std = np.sqrt(CHANNEL_NOISE_STD_MV**2 + THERMAL_NOISE_STD_MV**2) / np.sqrt(smoothing_window)
    return norm.ppf(1 - target_fpr) * effective_std


def simulate_detection_latency(magnitude_mv: float, n_trials: int, sample_interval_min: float,
                                smoothing_window: int, target_fpr: float, max_hours: float,
                                seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n_samples = int(max_hours * 60 / sample_interval_min)
    t_h = np.arange(n_samples) * sample_interval_min / 60.0
    true_signal = signal(t_h, magnitude_mv)
    threshold = false_positive_threshold(smoothing_window, target_fpr)

    latencies = np.full(n_trials, np.nan)
    for trial in range(n_trials):
        noise = rng.normal(0, CHANNEL_NOISE_STD_MV, n_samples) + rng.normal(0, THERMAL_NOISE_STD_MV, n_samples)
        readout = true_signal + noise
        smoothed = np.convolve(readout, np.ones(smoothing_window) / smoothing_window, mode="valid")
        crossed = np.where(smoothed > threshold)[0]
        if len(crossed) > 0:
            latencies[trial] = t_h[crossed[0] + smoothing_window - 1]
    return latencies


def main() -> None:
    print("=" * 72)
    print("DAMAGE-DETECTION TRIGGER: signal-grounded vs. assumed polling latency")
    print("=" * 72)
    print(f"Noise: channel={CHANNEL_NOISE_STD_MV}mV, thermal={THERMAL_NOISE_STD_MV}mV "
          f"(Acheron's existing 'Realistic biological noise' profile)")
    print(f"Signal rise: tau={RISE_TAU_H}h (reaches 95% of asymptote by 3h, per PMID 30799071)")
    print(f"Current assumption in regeneration_data_loss_window.py: "
          f"Normal({CURRENT_ASSUMPTION_MEAN_H}h, {CURRENT_ASSUMPTION_STD_H}h), min {CURRENT_ASSUMPTION_MIN_H}h\n")

    magnitudes_mv = [7.0, 21.0, 35.0, 70.0]  # 10%, 30%, 50%, 100% of the ~70mV V_HIGH-V_LOW range
    sample_interval_min = 5.0
    smoothing_window = 3  # 15-minute moving average
    target_fpr = 1e-3
    n_trials = 2000
    max_hours = 6.0

    results = {}
    for mag in magnitudes_mv:
        latencies = simulate_detection_latency(mag, n_trials, sample_interval_min, smoothing_window,
                                                 target_fpr, max_hours, seed=int(mag))
        detected = ~np.isnan(latencies)
        results[mag] = latencies
        if detected.sum() == 0:
            print(f"magnitude={mag:>5.1f}mV: never detected within {max_hours}h in any trial")
            continue
        print(f"magnitude={mag:>5.1f}mV ({100*mag/70:>3.0f}% of dynamic range): "
              f"detected in {100*detected.mean():.1f}% of trials, "
              f"median latency={np.nanmedian(latencies):.2f}h, "
              f"95th pct={np.nanpercentile(latencies, 95):.2f}h")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    for mag, latencies in results.items():
        valid = latencies[~np.isnan(latencies)]
        if len(valid) > 0:
            ax.hist(valid, bins=40, alpha=0.5, label=f"{mag:.0f}mV signal ({100*mag/70:.0f}% of range)",
                    range=(0, max_hours))
    ax.axvspan(CURRENT_ASSUMPTION_MIN_H,
               CURRENT_ASSUMPTION_MEAN_H + 2 * CURRENT_ASSUMPTION_STD_H,
               alpha=0.15, color="gray",
               label="current assumption's ~95% range (polling-based)")
    ax.set_xlabel("detection latency (hours)")
    ax.set_ylabel("trial count")
    ax.set_title("Signal-grounded detection latency vs. current polling assumption")
    ax.legend(fontsize=8)
    plt.tight_layout()
    out_path = ANALYSIS_DIR / "damage_detection_trigger.png"
    ANALYSIS_DIR.mkdir(exist_ok=True)
    plt.savefig(out_path, dpi=120)
    print(f"\nSaved figure: {out_path}")

    print("\n" + "=" * 72)
    print("INTERPRETATION")
    print("=" * 72)
    strong_mag = max(magnitudes_mv)
    weak_mag = min(magnitudes_mv)
    strong_median = np.nanmedian(results[strong_mag])
    weak_median = np.nanmedian(results[weak_mag])
    weak_p95 = np.nanpercentile(results[weak_mag], 95)

    print(f"Detection latency depends heavily on an assumed magnitude this repo cannot yet")
    print(f"  measure -- that dependence is the actual finding:")
    print(f"  - At full-range signal strength ({strong_mag:.0f}mV): median latency = {strong_median:.2f}h,")
    print(f"    FASTER than the current {CURRENT_ASSUMPTION_MEAN_H}h assumption. If the real signal turns out")
    print(f"    this strong, the existing polling-based assumption is safe, even conservative.")
    print(f"  - At 10% signal strength ({weak_mag:.0f}mV): median latency = {weak_median:.2f}h, 95th pct =")
    print(f"    {weak_p95:.2f}h -- {weak_median/CURRENT_ASSUMPTION_MEAN_H:.1f}x SLOWER than the current {CURRENT_ASSUMPTION_MEAN_H}h assumption at the")
    print(f"    median, and up to {weak_p95/CURRENT_ASSUMPTION_MEAN_H:.1f}x slower in the worst 5% of cases. If the real signal")
    print(f"    is this weak, the current assumption dangerously UNDERSTATES the vulnerability")
    print(f"    window regeneration_data_loss_window.py's redundancy math is built on.")
    print(f"  - The crossover is somewhere between 30% and 10% signal strength: at 30% ({magnitudes_mv[1]:.0f}mV),")
    print(f"    median latency ({np.nanmedian(results[magnitudes_mv[1]]):.2f}h) already roughly matches the current")
    print(f"    {CURRENT_ASSUMPTION_MEAN_H}h assumption -- so the current assumption is only as good as this")
    print(f"    unmeasured magnitude turns out to be.")
    print(f"\nWhat this does NOT show: the actual wound-depolarization magnitude for this system --")
    print(f"  that's the concrete, falsifiable thing a real measurement (voltage-sensitive dye")
    print(f"  imaging at a fresh wound site, exactly as Experiment A's protocol already plans to")
    print(f"  use) would need to pin down before this detection-latency estimate can replace the")
    print(f"  current placeholder with confidence.")
    print("=" * 72)


if __name__ == "__main__":
    main()
