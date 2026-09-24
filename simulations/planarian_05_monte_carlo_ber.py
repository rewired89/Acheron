"""
Acheron Simulation 4: Monte Carlo Bit Error Rate (BER)
=======================================================

PURPOSE:
The persistence simulator runs once with ideal parameters and reports
"integrity > 70% after 24 hours." That single run tells you nothing about
reliability distributions, tail risks, or what happens across thousands of
storage operations.

This simulation runs 1000 independent trials with realistic biological
noise and variability, giving true probability distributions for:
- How long each bit remains reliably readable
- What fraction of bits fail within 24h, 48h, 72h
- How much RAID redundancy is needed to achieve 99.9% reliability

METHODOLOGY:
Each Monte Carlo trial draws independent samples for:
- Cell-to-cell R_mem and g_gap variability (log-normal, CV=25%)
- Ion channel shot noise per timestep (Gaussian, σ=5 mV)
- Metabolic noise fraction (uniform 5–15%)
- Write fidelity (some cells fail to reach target voltage)

BIT ERROR DEFINITION:
A bit is in ERROR when the majority-vote voltage of its cell cluster
crosses the decision boundary (V_mid = -45 mV) at any point after write.

ERROR CORRECTION MODEL:
3× redundancy (Bio-RAID): bit is readable if ≥2 of 3 copies are correct
5× redundancy:             bit is readable if ≥3 of 5 copies are correct

OUTPUT:
- BER curves over time (mean ± 95% CI) for 1×, 3×, 5× redundancy
- Time-to-failure distribution (histogram)
- Probability of data survival at 24h, 48h, 72h
- Required redundancy for 99.9% reliability at each time point
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Dict, Tuple
from dataclasses import dataclass
import os
import time


# ─────────────────────────────────────────────
# Simulation parameters
# ─────────────────────────────────────────────

# Voltage levels
V_REST  = -50.0
V_HIGH  = -10.0
V_LOW   = -80.0
V_MID   = (V_HIGH + V_LOW) / 2.0   # -45.0 mV — decision boundary

# Per-bit cell cluster
CELLS_PER_BIT   = 9    # 3×3 cluster
CLUSTER_ROWS    = 3
CLUSTER_COLS    = 3

# Biophysical base parameters
G_GAP_BASE  = 0.005   # nS
R_MEM_BASE  = 200.0   # MΩ
TAU_BASE    = 240.0   # min
C_MEM       = 5.0     # μF/cm²
DT          = 1.0     # min (coarser timestep for speed in Monte Carlo)

# Noise parameters (realistic biological estimates)
CELL_CV             = 0.25   # 25% coefficient of variation for cell properties
CHANNEL_NOISE_STD   = 5.0    # mV per sqrt(min)
METABOLIC_NOISE_MIN = 0.05   # fraction
METABOLIC_NOISE_MAX = 0.15   # fraction
WRITE_FIDELITY_P    = 0.85   # probability each cell reaches target voltage on write


# ─────────────────────────────────────────────
# Single-bit trial
# ─────────────────────────────────────────────

class SingleBitTrial:
    """
    Simulates one bit stored in CELLS_PER_BIT cells with noise.
    Returns a time-series of bit correctness.
    """

    def __init__(self, bit_value: int, seed: int = None):
        if seed is not None:
            np.random.seed(seed)

        self.bit_value  = bit_value
        self.target_V   = V_HIGH if bit_value == 1 else V_LOW

        # Per-cell properties — log-normal variability
        sigma = np.sqrt(np.log(1 + CELL_CV**2))
        mu_r  = np.log(R_MEM_BASE) - 0.5 * sigma**2
        mu_g  = np.log(G_GAP_BASE) - 0.5 * sigma**2

        self.R_mem = np.random.lognormal(mu_r, sigma, CELLS_PER_BIT)
        self.g_gap = np.random.lognormal(mu_g, sigma, CELLS_PER_BIT)

        # Metabolic noise fraction — varies between cells
        self.meta_noise = np.random.uniform(
            METABOLIC_NOISE_MIN, METABOLIC_NOISE_MAX, CELLS_PER_BIT)

        # Write with imperfect fidelity
        # Each cell independently reaches target with probability WRITE_FIDELITY_P
        self.V = np.where(
            np.random.random(CELLS_PER_BIT) < WRITE_FIDELITY_P,
            self.target_V,
            V_REST   # failed cell starts at rest
        )

    def step(self):
        """One timestep: gap current (simplified mean-field) + membrane + noise."""
        # Mean-field gap junction: each cell pulled toward cluster mean voltage
        V_mean = np.mean(self.V)
        I_gap  = self.g_gap * (V_mean - self.V)

        # Membrane leak
        I_mem = (V_REST - self.V) / (self.R_mem * TAU_BASE)
        # Metabolic noise on membrane current
        I_mem *= (1.0 + np.random.uniform(-self.meta_noise, self.meta_noise,
                                           CELLS_PER_BIT))

        dV = (I_gap + I_mem) / C_MEM * DT

        # Ion channel shot noise
        dV += np.random.normal(0, CHANNEL_NOISE_STD * np.sqrt(DT),
                               CELLS_PER_BIT)

        self.V += dV
        np.clip(self.V, -120.0, 60.0, out=self.V)

    def is_readable(self) -> bool:
        """Majority vote: is the cluster voltage on the correct side of V_mid?"""
        V_mean = np.mean(self.V)
        if self.bit_value == 1:
            return V_mean > V_MID
        else:
            return V_mean < V_MID

    def run(self, duration_hours: float,
            checkpoint_hours: List[float]) -> Dict:
        """
        Run for duration_hours, recording correctness at checkpoints.

        Returns:
            Dict mapping checkpoint_hour → bool (readable)
            and 'failure_hour' → first hour when bit became unreadable (or None)
        """
        n_steps        = int(duration_hours * 60 / DT)
        ckpt_steps     = {int(h * 60 / DT): h for h in checkpoint_hours}
        correctness    = {}
        failure_hour   = None

        for step in range(n_steps):
            self.step()
            h = (step + 1) * DT / 60.0

            if step in ckpt_steps:
                ok = self.is_readable()
                correctness[ckpt_steps[step]] = ok

            if failure_hour is None and not self.is_readable():
                failure_hour = h

        return {'correctness': correctness, 'failure_hour': failure_hour}


# ─────────────────────────────────────────────
# RAID redundancy model
# ─────────────────────────────────────────────

def apply_raid(trials: List[Dict], redundancy: int,
               checkpoints: List[float]) -> Dict[float, float]:
    """
    Apply N-way majority vote redundancy to a list of bit trials.

    Args:
        trials:     List of single-bit trial results (must be multiple of redundancy)
        redundancy: 1, 3, or 5
        checkpoints: Time points to evaluate

    Returns:
        Dict of checkpoint → P(bit readable) after RAID
    """
    n_groups = len(trials) // redundancy
    raid_correctness = {h: [] for h in checkpoints}

    for g in range(n_groups):
        group = trials[g * redundancy: (g + 1) * redundancy]
        for h in checkpoints:
            votes   = [t['correctness'].get(h, False) for t in group]
            # Majority vote: need >50% of copies readable
            correct = sum(votes) > redundancy / 2.0
            raid_correctness[h].append(correct)

    return {h: np.mean(v) for h, v in raid_correctness.items()}


# ─────────────────────────────────────────────
# Main Monte Carlo runner
# ─────────────────────────────────────────────

def run_monte_carlo(
        n_trials: int = 1000,
        duration_hours: float = 72.0,
        checkpoints: List[float] = None,
        redundancy_levels: List[int] = None,
        output_dir: str = 'analysis') -> Dict:
    """
    Run Monte Carlo BER analysis.

    Args:
        n_trials:          Total independent bit trials (per redundancy level)
        duration_hours:    Total simulation duration
        checkpoints:       Hours at which to measure BER
        redundancy_levels: RAID levels to compare
        output_dir:        Where to save plots

    Returns:
        Full results dictionary
    """
    os.makedirs(output_dir, exist_ok=True)

    if checkpoints is None:
        checkpoints = [6, 12, 18, 24, 36, 48, 60, 72]
    if redundancy_levels is None:
        redundancy_levels = [1, 3, 5]

    # Ensure n_trials is divisible by max redundancy
    max_redundancy = max(redundancy_levels)
    n_trials = (n_trials // max_redundancy) * max_redundancy

    print("=" * 65)
    print("ACHERON MONTE CARLO BER ANALYSIS")
    print("=" * 65)
    print(f"Trials: {n_trials} | Duration: {duration_hours}h | "
          f"Redundancy levels: {redundancy_levels}")
    print(f"Noise: channel σ={CHANNEL_NOISE_STD}mV, cell CV={CELL_CV:.0%}, "
          f"metabolic={METABOLIC_NOISE_MIN:.0%}–{METABOLIC_NOISE_MAX:.0%}")
    print()

    t0 = time.time()

    # Run all trials (alternating bit values for balanced test)
    all_trials = []
    for trial_idx in range(n_trials):
        bit_value = trial_idx % 2  # alternate 0 and 1
        bit = SingleBitTrial(bit_value, seed=trial_idx)
        result = bit.run(duration_hours, checkpoints)
        all_trials.append(result)

        if (trial_idx + 1) % 100 == 0:
            pct = (trial_idx + 1) / n_trials * 100
            print(f"  Progress: {pct:.0f}% ({trial_idx + 1}/{n_trials}) "
                  f"| {time.time()-t0:.0f}s elapsed")

    print(f"  Done in {time.time()-t0:.1f}s")

    # ── Collect failure times ───────────────────────────────────────────
    failure_hours = [t['failure_hour'] for t in all_trials
                     if t['failure_hour'] is not None]
    never_failed  = sum(1 for t in all_trials if t['failure_hour'] is None)

    # ── Apply RAID redundancy ───────────────────────────────────────────
    raid_results = {}
    for r in redundancy_levels:
        raid_results[r] = apply_raid(all_trials, r, checkpoints)

    # ── BER = 1 - P(readable) ──────────────────────────────────────────
    ber_by_redundancy = {}
    for r in redundancy_levels:
        ber_by_redundancy[r] = {h: 1.0 - p for h, p in raid_results[r].items()}

    # ── Bootstrap confidence intervals for 1× ──────────────────────────
    n_boot  = 200
    boot_ber = {h: [] for h in checkpoints}
    for _ in range(n_boot):
        sample_idx = np.random.randint(0, n_trials, n_trials)
        sample     = [all_trials[i] for i in sample_idx]
        for h in checkpoints:
            correct_frac = np.mean([t['correctness'].get(h, False)
                                    for t in sample])
            boot_ber[h].append(1.0 - correct_frac)

    ber_ci_low  = {h: np.percentile(boot_ber[h], 2.5)  for h in checkpoints}
    ber_ci_high = {h: np.percentile(boot_ber[h], 97.5) for h in checkpoints}

    results = {
        'all_trials':          all_trials,
        'failure_hours':       failure_hours,
        'never_failed':        never_failed,
        'raid_results':        raid_results,
        'ber_by_redundancy':   ber_by_redundancy,
        'ber_ci_low':          ber_ci_low,
        'ber_ci_high':         ber_ci_high,
        'checkpoints':         checkpoints,
        'n_trials':            n_trials,
        'redundancy_levels':   redundancy_levels,
    }

    _plot_ber(results, output_dir)
    _print_ber_summary(results)

    return results


# ─────────────────────────────────────────────
# Plotting
# ─────────────────────────────────────────────

def _plot_ber(results: Dict, output_dir: str):
    fig = plt.figure(figsize=(18, 12))
    fig.suptitle("Acheron Monte Carlo BER Analysis\n"
                 "Realistic bit error rate with biological noise (1000 trials)",
                 fontsize=13, fontweight='bold')

    gs   = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)
    axes = [fig.add_subplot(gs[i // 3, i % 3]) for i in range(6)]

    ckpts   = results['checkpoints']
    colors  = {1: '#e74c3c', 3: '#f39c12', 5: '#2ecc71'}
    n_tri   = results['n_trials']

    # Panel 1: BER over time by redundancy level
    ax = axes[0]
    for r in results['redundancy_levels']:
        ber_vals = [results['ber_by_redundancy'][r][h] for h in ckpts]
        label    = f'{r}× redundancy (Bio-RAID x{r})'
        ax.semilogy(ckpts, np.maximum(ber_vals, 1e-4),
                    '-o', color=colors[r], linewidth=2,
                    markersize=6, label=label)

    # CI for 1× only
    ber_low  = [results['ber_ci_low'][h]  for h in ckpts]
    ber_high = [results['ber_ci_high'][h] for h in ckpts]
    ax.fill_between(ckpts, np.maximum(ber_low, 1e-4),
                    np.maximum(ber_high, 1e-4),
                    color=colors[1], alpha=0.15, label='1× 95% CI')

    ax.axhline(1e-3, color='black', linestyle='--', linewidth=1,
               label='10⁻³ target BER')
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Bit Error Rate (BER)')
    ax.set_title('BER Over Time\nby Redundancy Level')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, which='both')
    ax.set_ylim(bottom=1e-4)

    # Panel 2: Time-to-failure histogram
    ax = axes[1]
    fh = results['failure_hours']
    if fh:
        ax.hist(fh, bins=40, color='coral', edgecolor='darkred', alpha=0.8)
        ax.axvline(np.median(fh), color='black', linestyle='--',
                   linewidth=2, label=f'Median: {np.median(fh):.1f}h')
        ax.axvline(np.percentile(fh, 5), color='red', linestyle=':',
                   linewidth=1.5, label=f'5th pct: {np.percentile(fh, 5):.1f}h')

    nf_pct = results['never_failed'] / n_tri * 100
    ax.set_xlabel('Time of First Bit Error (hours)')
    ax.set_ylabel('Count (out of trials that failed)')
    ax.set_title(f'Time-to-First-Failure Distribution\n'
                 f'({nf_pct:.1f}% never failed in {ckpts[-1]}h)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 3: P(survival) vs time
    ax = axes[2]
    for r in results['redundancy_levels']:
        survival = [results['raid_results'][r][h] for h in ckpts]
        ax.plot(ckpts, survival, '-o', color=colors[r], linewidth=2,
                markersize=6, label=f'{r}× RAID')
    ax.axhline(0.999, color='black', linestyle='--', linewidth=1,
               label='99.9% target')
    ax.axhline(0.99,  color='gray',  linestyle=':', linewidth=1,
               label='99% threshold')
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('P(bit still readable)')
    ax.set_title('Data Survival Probability\nvs Time and Redundancy')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.8, 1.01)

    # Panel 4: Required redundancy for 99.9% at each checkpoint
    ax = axes[3]
    target   = 0.999
    req_redundancy = []
    for h in ckpts:
        needed = None
        for r in sorted(results['redundancy_levels']):
            if results['raid_results'][r][h] >= target:
                needed = r
                break
        req_redundancy.append(needed if needed else max(results['redundancy_levels']) + 2)

    ax.bar(ckpts, req_redundancy, color='steelblue', alpha=0.8, width=3)
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Minimum Redundancy Required')
    ax.set_title('Redundancy Required for 99.9% Reliability\nat Each Time Point')
    ax.set_ylim(0, max(results['redundancy_levels']) + 3)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.grid(True, alpha=0.3, axis='y')

    for x, y in zip(ckpts, req_redundancy):
        label = f'{y}×' if y <= max(results['redundancy_levels']) else '>5×'
        ax.text(x, y + 0.1, label, ha='center', va='bottom', fontsize=9)

    # Panel 5: BER at 24h for different noise scenarios
    ax = axes[4]
    noise_labels  = ['Ideal\n(0 noise)', 'Mild\n(σ=2mV)', 'Realistic\n(σ=5mV)',
                     'Severe\n(σ=10mV)']
    noise_stds    = [0.0, 2.0, 5.0, 10.0]
    ber_24h_per_noise = []

    for ns in noise_stds:
        n_mini = 200
        trials_mini = []
        for ti in range(n_mini):
            import importlib, sys
            # Inline a quick mini-run with different noise
            orig_std = globals().get('CHANNEL_NOISE_STD', 5.0)
            # Patch noise for this run
            bv   = ti % 2
            bit  = SingleBitTrial.__new__(SingleBitTrial)
            bit.bit_value = bv
            bit.target_V  = V_HIGH if bv == 1 else V_LOW
            np.random.seed(ti + 500)
            sigma = np.sqrt(np.log(1 + CELL_CV**2))
            mu_r  = np.log(R_MEM_BASE) - 0.5 * sigma**2
            mu_g  = np.log(G_GAP_BASE) - 0.5 * sigma**2
            bit.R_mem      = np.random.lognormal(mu_r, sigma, CELLS_PER_BIT)
            bit.g_gap      = np.random.lognormal(mu_g, sigma, CELLS_PER_BIT)
            bit.meta_noise = np.random.uniform(METABOLIC_NOISE_MIN,
                                               METABOLIC_NOISE_MAX, CELLS_PER_BIT)
            bit.V = np.where(
                np.random.random(CELLS_PER_BIT) < WRITE_FIDELITY_P,
                bit.target_V, V_REST)

            # Manually run with patched noise std
            n_steps = int(24.0 * 60 / DT)
            failed  = False
            for _ in range(n_steps):
                V_mean = np.mean(bit.V)
                I_gap  = bit.g_gap * (V_mean - bit.V)
                I_mem  = (V_REST - bit.V) / (bit.R_mem * TAU_BASE)
                I_mem *= (1.0 + np.random.uniform(-bit.meta_noise,
                                                   bit.meta_noise, CELLS_PER_BIT))
                dV  = (I_gap + I_mem) / C_MEM * DT
                dV += np.random.normal(0, ns * np.sqrt(DT), CELLS_PER_BIT)
                bit.V += dV
                np.clip(bit.V, -120.0, 60.0, out=bit.V)

            readable = (np.mean(bit.V) > V_MID) if bv == 1 else (np.mean(bit.V) < V_MID)
            trials_mini.append(not readable)

        ber_24h_per_noise.append(np.mean(trials_mini))

    bar_colors = ['green', 'blue', 'orange', 'red']
    bars = ax.bar(noise_labels, ber_24h_per_noise,
                  color=bar_colors, alpha=0.8)
    ax.axhline(0.001, color='black', linestyle='--', label='10⁻³ target')
    ax.set_ylabel('BER at 24 hours')
    ax.set_title('BER at 24h vs Channel Noise Level\n(1× redundancy, 200 trials each)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')

    for bar, val in zip(bars, ber_24h_per_noise):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + max(ber_24h_per_noise)*0.01,
                f'{val:.1%}', ha='center', va='bottom', fontsize=9,
                fontweight='bold')

    # Panel 6: 24h reliability summary table
    ax = axes[5]
    ax.axis('off')
    rows = []
    rows.append(['Metric', 'Value'])
    rows.append(['Total trials', str(results['n_trials'])])
    rows.append(['Never failed (72h)', f"{results['never_failed']/results['n_trials']:.1%}"])
    if results['failure_hours']:
        rows.append(['Median TTF', f"{np.median(results['failure_hours']):.1f}h"])
        rows.append(['5th pct TTF', f"{np.percentile(results['failure_hours'], 5):.1f}h"])
    for r in results['redundancy_levels']:
        p_24h = results['raid_results'][r].get(24, float('nan'))
        rows.append([f'{r}× RAID survive 24h', f'{p_24h:.3%}'])
    for r in results['redundancy_levels']:
        p_72h = results['raid_results'][r].get(72, float('nan'))
        rows.append([f'{r}× RAID survive 72h', f'{p_72h:.3%}'])

    table_data  = [[r[1]] for r in rows[1:]]
    row_labels  = [r[0] for r in rows[1:]]
    tbl = ax.table(cellText=table_data, rowLabels=row_labels,
                   colLabels=['Value'], cellLoc='center',
                   loc='center', bbox=[0, 0, 1, 1])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    ax.set_title('Summary Statistics', fontweight='bold')

    path = os.path.join(output_dir, 'monte_carlo_ber.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {path}")
    plt.close(fig)


def _print_ber_summary(results: Dict):
    print()
    print("=" * 65)
    print("MONTE CARLO BER ANALYSIS — SUMMARY")
    print("=" * 65)
    print(f"{'':30} {'1× RAID':>10} {'3× RAID':>10} {'5× RAID':>10}")
    print("-" * 65)

    for h in results['checkpoints']:
        row = f"P(survive {h:3.0f}h)"
        for r in results['redundancy_levels']:
            p = results['raid_results'][r].get(h, 0)
            row += f"   {p:>8.3%}"
        print(row)

    print()
    print("INTERPRETATION:")
    print("  If 3× RAID does not reach 99% survival at 24h with")
    print("  realistic noise (σ=5mV), the storage system needs either:")
    print("  (a) Lower noise — better cell line, more stable culture")
    print("  (b) Higher redundancy — 5× or more copies per bit")
    print("  (c) More frequent refresh — silicon re-encodes before bit drifts")
    print()
    print("  Key design output: use these numbers to set the")
    print("  silicon controller's SCRUB INTERVAL (days between re-encoding)")
    print("=" * 65)


if __name__ == '__main__':
    run_monte_carlo(
        n_trials=1000,
        duration_hours=72.0,
        checkpoints=[6, 12, 18, 24, 36, 48, 60, 72],
        redundancy_levels=[1, 3, 5],
    )
