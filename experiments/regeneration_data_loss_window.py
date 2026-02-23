"""
Acheron Simulation 5: Regeneration Data Loss Window
=====================================================

PURPOSE:
The Bio-RAID architecture assumes that when a tile fails, the biology
regenerates it and the silicon controller re-encodes it from a redundant copy.
But regeneration takes time — and during that window, the system is running
on degraded redundancy.

The current Bio-RAID simulator uses abstract degradation rates. This simulation
models the REAL timeline with biologically grounded timing distributions.

THE CRITICAL WINDOW:
  t=0:         Tile cells die (radiation hit, necrosis, mechanical damage)
  t+0 to 30m:  Silicon controller polls voltage imaging → detects failure
  t+2 to 8h:   Neoblasts mobilize and migrate to damage site
  t+6 to 24h:  New cells divide, differentiate, mature
  t+24 to 25h: Silicon controller re-encodes new cells via optogenetics
  → Total: 24–33h vulnerable window

During this window, the system is running with N-1 copies of the redundant data.
If a second tile fails in that window, you lose another copy.
Depending on redundancy level, this may cause DATA LOSS.

KEY QUESTIONS:
1. What is P(data loss) vs redundancy level during the repair window?
2. What tile failure rate makes the system unsafe at 3× redundancy?
3. What redundancy is required for 99.9% data integrity over 1 year?

MODEL:
- Tile failure: Poisson process with configurable rate (λ failures/tile/day)
- Detection latency: Normal(30 min, 10 min) truncated at 5 min
- Neoblast migration: Log-normal(μ=4h, σ=1.5h) — faster for smaller wounds
- Cell maturation: Normal(12h, 3h) truncated at 6h
- Re-encoding: fixed 1h (silicon controller operation)
- Total repair window: sum of above components

REDUNDANCY STRATEGY:
- 3× RAID:  data recoverable if ≥2 of 3 copies available
- 5× RAID:  data recoverable if ≥3 of 5 copies available
- 7× RAID:  data recoverable if ≥4 of 7 copies available

OUTPUT:
- P(data loss during repair window) vs failure rate and redundancy
- Expected repair window duration distribution
- Safe operating envelope: tile failure rate vs required redundancy
- Year-long data integrity projection
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dataclasses import dataclass
from typing import List, Dict, Tuple
import os


# ─────────────────────────────────────────────
# Timing distributions (biologically grounded)
# ─────────────────────────────────────────────

@dataclass
class RegenerationTimingModel:
    """
    Probability distributions for each phase of the repair timeline.

    All times in hours unless noted.
    """
    # Detection latency: silicon polls voltage imaging on a schedule
    detection_mean_h:   float = 0.5    # 30 min polling interval
    detection_std_h:    float = 0.17   # ±10 min variability
    detection_min_h:    float = 0.08   # 5 min minimum (can't detect instantly)

    # Neoblast migration to wound site
    # In S. mediterranea: wound signals trigger mobilization within 30 min,
    # cells arrive at small wounds in 2–6h, larger wounds 6–12h
    migration_mean_h:  float = 4.0    # log-normal mean
    migration_sigma_h: float = 1.5    # log-normal std (in log-space ≈ σ_ln)

    # New cell maturation: divide + differentiate + establish gap junctions
    # Conservative estimate: planarian neoblasts → postmitotic daughter in 6–24h
    maturation_mean_h: float = 12.0
    maturation_std_h:  float = 3.0
    maturation_min_h:  float = 6.0

    # Silicon re-encoding operation (DMD write + verification)
    reencode_fixed_h:  float = 1.0    # deterministic (controlled by hardware)

    def sample_repair_window(self, n: int = 1, seed: int = None) -> np.ndarray:
        """
        Sample total repair window durations.

        Returns: array of shape (n,) with repair times in hours
        """
        if seed is not None:
            np.random.seed(seed)

        # Detection latency (truncated normal)
        t_detect = np.random.normal(self.detection_mean_h,
                                     self.detection_std_h, n)
        t_detect = np.maximum(t_detect, self.detection_min_h)

        # Neoblast migration (log-normal)
        # Parameterize log-normal from mean and sigma_ln
        sigma_ln   = self.migration_sigma_h
        mu_ln      = np.log(self.migration_mean_h) - 0.5 * sigma_ln**2
        t_migrate  = np.random.lognormal(mu_ln, sigma_ln, n)

        # Maturation (truncated normal)
        t_mature   = np.random.normal(self.maturation_mean_h,
                                       self.maturation_std_h, n)
        t_mature   = np.maximum(t_mature, self.maturation_min_h)

        # Re-encoding (fixed)
        t_reencode = np.full(n, self.reencode_fixed_h)

        return t_detect + t_migrate + t_mature + t_reencode


# ─────────────────────────────────────────────
# RAID state model
# ─────────────────────────────────────────────

class RAIDStateSimulator:
    """
    Simulates a RAID group of tiles over time.

    Models:
    - Tile failures as Poisson process
    - Repair windows for each failed tile
    - Data loss when too many tiles fail simultaneously
    """

    def __init__(self,
                 n_copies: int,
                 min_copies_for_read: int,
                 failure_rate_per_day: float,
                 timing: RegenerationTimingModel = None):
        """
        Args:
            n_copies:              Total copies (3, 5, or 7)
            min_copies_for_read:   Minimum copies available to read data
            failure_rate_per_day:  λ failures per tile per day (Poisson)
            timing:                Regeneration timing model
        """
        self.n_copies             = n_copies
        self.min_copies           = min_copies_for_read
        self.failure_rate         = failure_rate_per_day
        self.timing               = timing or RegenerationTimingModel()

    def simulate_year(self, n_trials: int = 5000,
                      seed: int = None) -> Dict:
        """
        Monte Carlo: simulate n_trials RAID groups over 365 days.

        Returns:
            Dict with P(data loss), expected outage count, etc.
        """
        if seed is not None:
            np.random.seed(seed)

        duration_days  = 365.0
        data_lost_count = 0
        first_loss_days = []
        max_concurrent_failures = []

        for trial in range(n_trials):
            # Generate failure events for all tiles (Poisson)
            # Each tile fails independently at rate failure_rate_per_day
            failure_times = []
            for tile in range(self.n_copies):
                # Poisson process: inter-arrival times ~ Exponential
                t = 0.0
                while t < duration_days:
                    t += np.random.exponential(1.0 / self.failure_rate)
                    if t < duration_days:
                        failure_times.append(t)

            failure_times.sort()

            # For each failure, sample a repair window
            n_failures = len(failure_times)
            if n_failures == 0:
                max_concurrent_failures.append(0)
                continue

            repair_windows = self.timing.sample_repair_window(n=n_failures)
            repair_end_times = np.array(failure_times) + repair_windows / 24.0

            # Scan timeline: count copies available at each failure event
            data_lost_this_trial = False
            first_loss_day       = None
            max_concurrent       = 0

            for fi, (fail_t, repair_t) in enumerate(zip(failure_times,
                                                         repair_end_times)):
                # Count tiles UNAVAILABLE at the moment of this failure
                # (i.e., other tiles that failed before this and not yet repaired)
                unavailable = sum(
                    1 for fj, (f, r) in enumerate(
                        zip(failure_times, repair_end_times))
                    if fj != fi
                    and f <= fail_t       # failed before this event
                    and r > fail_t        # not yet repaired
                )
                concurrent = unavailable + 1  # include this tile
                max_concurrent = max(max_concurrent, concurrent)

                # Available = total - concurrent unavailable
                available = self.n_copies - concurrent

                if available < self.min_copies:
                    data_lost_this_trial = True
                    if first_loss_day is None:
                        first_loss_day = fail_t
                    break

            if data_lost_this_trial:
                data_lost_count += 1
                first_loss_days.append(first_loss_day)

            max_concurrent_failures.append(max_concurrent)

        p_loss = data_lost_count / n_trials
        return {
            'p_data_loss':             p_loss,
            'p_data_safe':             1.0 - p_loss,
            'first_loss_days':         first_loss_days,
            'max_concurrent_mean':     np.mean(max_concurrent_failures),
            'max_concurrent_max':      np.max(max_concurrent_failures),
            'n_trials':                n_trials,
        }


# ─────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────

def run_regeneration_analysis(
        n_trials: int = 3000,
        output_dir: str = 'analysis') -> Dict:

    os.makedirs(output_dir, exist_ok=True)

    print("=" * 65)
    print("ACHERON REGENERATION DATA LOSS WINDOW ANALYSIS")
    print("=" * 65)

    timing = RegenerationTimingModel()

    # ── Visualize repair window distribution ─────────────────────────
    repair_samples = timing.sample_repair_window(n=10000, seed=42)
    print(f"Repair window statistics:")
    print(f"  Mean:   {np.mean(repair_samples):.1f}h")
    print(f"  Median: {np.median(repair_samples):.1f}h")
    print(f"  5th pct: {np.percentile(repair_samples, 5):.1f}h")
    print(f"  95th pct: {np.percentile(repair_samples, 95):.1f}h")

    # ── RAID configurations ───────────────────────────────────────────
    raid_configs = [
        (3, 2, '3× RAID (need ≥2)'),
        (5, 3, '5× RAID (need ≥3)'),
        (7, 4, '7× RAID (need ≥4)'),
    ]

    # ── Failure rate sweep ────────────────────────────────────────────
    # What is a realistic tile failure rate?
    # Biological cell death: ~0.1–1% per day in culture
    # Radiation environment: can be orders of magnitude higher
    failure_rates = [0.001, 0.005, 0.01, 0.05, 0.10, 0.20, 0.50]

    print(f"\nRunning P(data loss over 1 year) vs failure rate ...")
    print(f"{'Failure rate/day':>18} {'3× RAID':>12} {'5× RAID':>12} {'7× RAID':>12}")
    print("-" * 60)

    results_by_config = {label: [] for _, _, label in raid_configs}

    for fr in failure_rates:
        row = f"  {fr:.3f}/day "
        for n_copies, min_copies, label in raid_configs:
            sim = RAIDStateSimulator(n_copies, min_copies, fr, timing)
            result = sim.simulate_year(n_trials=n_trials, seed=42)
            results_by_config[label].append(result['p_data_loss'])
            row += f"   {result['p_data_loss']:>9.3%}"
        print(row)

    # ── Repair window phase breakdown ─────────────────────────────────
    n_samp = 5000
    np.random.seed(42)

    t_detect = np.maximum(np.random.normal(timing.detection_mean_h,
                                            timing.detection_std_h, n_samp),
                          timing.detection_min_h)

    sigma_ln = timing.migration_sigma_h
    mu_ln    = np.log(timing.migration_mean_h) - 0.5 * sigma_ln**2
    t_migrate = np.random.lognormal(mu_ln, sigma_ln, n_samp)

    t_mature  = np.maximum(np.random.normal(timing.maturation_mean_h,
                                             timing.maturation_std_h, n_samp),
                           timing.maturation_min_h)
    t_encode  = np.full(n_samp, timing.reencode_fixed_h)
    t_total   = t_detect + t_migrate + t_mature + t_encode

    # ── Plot ──────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 14))
    fig.suptitle("Acheron Regeneration Data Loss Window Analysis\n"
                 "What is the risk during biological repair?",
                 fontsize=13, fontweight='bold')

    gs   = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)
    axes = [fig.add_subplot(gs[i // 3, i % 3]) for i in range(6)]

    colors = {'3× RAID (need ≥2)': '#e74c3c',
              '5× RAID (need ≥3)': '#f39c12',
              '7× RAID (need ≥4)': '#2ecc71'}

    # Panel 1: Repair window distribution
    ax = axes[0]
    phase_data = [t_detect, t_migrate, t_mature, t_encode]
    phase_labels = ['Detection\n(polling)', 'Neoblast\nmigration',
                    'Cell\nmaturation', 'Silicon\nre-encode']
    phase_colors = ['#3498db', '#e67e22', '#9b59b6', '#1abc9c']

    bp = ax.boxplot(phase_data, patch_artist=True,
                    medianprops={'color': 'black', 'linewidth': 2})
    for patch, color in zip(bp['boxes'], phase_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    ax.set_xticklabels(phase_labels, fontsize=9)
    ax.set_ylabel('Duration (hours)')
    ax.set_title('Repair Timeline Phase Breakdown\n(10,000 sampled repairs)')
    ax.grid(True, alpha=0.3, axis='y')

    # Add total line
    ax2_twin = ax.twinx()
    ax2_twin.plot([], [], 'k--', label=f'Total: {np.mean(t_total):.1f}h mean')
    ax2_twin.set_yticks([])
    ax.text(0.98, 0.98, f'Total repair:\n{np.mean(t_total):.1f}h mean\n'
            f'{np.percentile(t_total, 95):.1f}h 95th pct',
            transform=ax.transAxes, ha='right', va='top',
            fontsize=9, bbox=dict(boxstyle='round', facecolor='lightyellow',
                                   alpha=0.8))

    # Panel 2: Total repair window histogram
    ax = axes[1]
    ax.hist(t_total, bins=60, color='steelblue', edgecolor='navy',
            alpha=0.8, density=True)
    ax.axvline(np.mean(t_total),  color='black', linestyle='-',
               linewidth=2, label=f'Mean: {np.mean(t_total):.1f}h')
    ax.axvline(np.median(t_total), color='gray', linestyle='--',
               linewidth=1.5, label=f'Median: {np.median(t_total):.1f}h')
    ax.axvline(np.percentile(t_total, 95), color='red', linestyle=':',
               linewidth=1.5, label=f'95th pct: {np.percentile(t_total, 95):.1f}h')
    ax.set_xlabel('Total Repair Window (hours)')
    ax.set_ylabel('Density')
    ax.set_title('Total Repair Window Distribution\n'
                 '(detection + migration + maturation + re-encode)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 3: P(data loss) vs failure rate
    ax = axes[2]
    for label, p_loss_list in results_by_config.items():
        ax.semilogy(failure_rates, [max(p, 1e-5) for p in p_loss_list],
                    '-o', color=colors[label], linewidth=2,
                    markersize=6, label=label)
    ax.axhline(0.001, color='black', linestyle='--',
               linewidth=1.5, label='0.1% loss threshold')
    ax.axvline(0.01, color='gray', linestyle=':',
               linewidth=1.5, label='Realistic cell death rate\n(~1%/day in culture)')
    ax.set_xlabel('Tile Failure Rate (failures/tile/day)')
    ax.set_ylabel('P(Data Loss in 365 days)')
    ax.set_title('Annual Data Loss Risk\nvs Tile Failure Rate')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, which='both')

    # Panel 4: Safe operating envelope
    ax = axes[3]
    target_p_loss = 0.001   # 0.1% annual loss = acceptable
    safe_rates    = {}
    for label, p_loss_list in results_by_config.items():
        safe = [failure_rates[i] for i, p in enumerate(p_loss_list)
                if p <= target_p_loss]
        safe_rates[label] = max(safe) if safe else 0.0

    raid_names = list(safe_rates.keys())
    max_rates  = list(safe_rates.values())
    bar_colors = [colors[n] for n in raid_names]

    bars = ax.bar(range(len(raid_names)), max_rates,
                  color=bar_colors, alpha=0.85)
    ax.axhline(0.01, color='black', linestyle='--',
               label='Realistic culture rate (~1%/day)')
    ax.set_xticks(range(len(raid_names)))
    ax.set_xticklabels([n.replace(' (', '\n(') for n in raid_names],
                       fontsize=9)
    ax.set_ylabel('Max Safe Failure Rate (failures/tile/day)')
    ax.set_title(f'Safe Operating Envelope\n(for <0.1% annual data loss)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    for bar, val in zip(bars, max_rates):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, val * 1.05,
                    f'{val:.3f}/day', ha='center', va='bottom',
                    fontsize=9, fontweight='bold')

    # Panel 5: Time-to-first-loss distribution (5× RAID, realistic rate)
    ax = axes[4]
    sim_5x = RAIDStateSimulator(5, 3, 0.01, timing)
    result_5x = sim_5x.simulate_year(n_trials=5000, seed=123)

    if result_5x['first_loss_days']:
        ax.hist(result_5x['first_loss_days'], bins=40,
                color='orange', edgecolor='darkorange', alpha=0.85)
        ax.axvline(np.median(result_5x['first_loss_days']), color='black',
                   linestyle='--', linewidth=2,
                   label=f"Median: day {np.median(result_5x['first_loss_days']):.0f}")
        ax.axvline(365, color='green', linestyle=':',
                   linewidth=2, label='1 year mark')
    else:
        ax.text(0.5, 0.5, 'No data loss events\nin 5000 trials',
                ha='center', va='center', transform=ax.transAxes,
                fontsize=14, color='green', fontweight='bold')

    safe_pct = result_5x['p_data_safe'] * 100
    ax.set_xlabel('Day of First Data Loss Event')
    ax.set_ylabel('Count')
    ax.set_title(f'Time-to-First-Loss: 5× RAID\n'
                 f'(failure rate=1%/day, {safe_pct:.1f}% safe for full year)')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 6: Summary table
    ax = axes[5]
    ax.axis('off')

    table_rows = [
        ['Repair phase', 'Mean', '95th pct'],
        ['Detection',    f'{np.mean(t_detect):.1f}h',  f'{np.percentile(t_detect, 95):.1f}h'],
        ['Neoblast migration', f'{np.mean(t_migrate):.1f}h', f'{np.percentile(t_migrate, 95):.1f}h'],
        ['Cell maturation', f'{np.mean(t_mature):.1f}h', f'{np.percentile(t_mature, 95):.1f}h'],
        ['Re-encoding',  f'{timing.reencode_fixed_h:.1f}h', f'{timing.reencode_fixed_h:.1f}h'],
        ['TOTAL window', f'{np.mean(t_total):.1f}h', f'{np.percentile(t_total, 95):.1f}h'],
        ['', '', ''],
        ['RAID config', '1%/day P(safe 1yr)', 'Required for >99.9%'],
    ]
    for n_copies, min_copies, label in raid_configs:
        sim = RAIDStateSimulator(n_copies, min_copies, 0.01, timing)
        r = sim.simulate_year(n_trials=2000, seed=77)
        safe_redundancy = '✓ YES' if r['p_data_safe'] >= 0.999 else '✗ NO'
        table_rows.append([label, f"{r['p_data_safe']:.2%}", safe_redundancy])

    col_labels  = table_rows[0]
    cell_data   = table_rows[1:]
    tbl = ax.table(cellText=cell_data, colLabels=col_labels,
                   cellLoc='center', loc='center',
                   bbox=[0, 0, 1, 1])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    ax.set_title('Repair Window & RAID Summary', fontweight='bold')

    path = os.path.join(output_dir, 'regeneration_data_loss_window.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {path}")
    plt.close(fig)

    _print_final_summary(results_by_config, failure_rates, timing, t_total)

    return {
        'results_by_config': results_by_config,
        'failure_rates':     failure_rates,
        'repair_window_mean_h': np.mean(t_total),
    }


def _print_final_summary(results_by_config, failure_rates, timing, t_total):
    print()
    print("=" * 65)
    print("REGENERATION WINDOW ANALYSIS — SUMMARY")
    print("=" * 65)
    print(f"Expected repair window: {np.mean(t_total):.1f}h mean, "
          f"{np.percentile(t_total, 95):.1f}h (95th pct)")
    print()
    print("At realistic cell death rate (~1%/tile/day in culture):")

    for label, p_loss_list in results_by_config.items():
        # Find p_loss at 0.01 failure rate
        idx = failure_rates.index(0.01) if 0.01 in failure_rates else None
        if idx is not None:
            p_loss = p_loss_list[idx]
            status = "SAFE" if p_loss < 0.001 else "AT RISK"
            print(f"  {label}: P(data loss in 1 year) = {p_loss:.3%}  [{status}]")

    print()
    print("DESIGN RECOMMENDATIONS:")
    print("  → The silicon scrub interval should be < half the mean repair window")
    print(f"    → Target scrub every {np.mean(t_total)/2:.0f}h "
          f"({np.mean(t_total)/2/24:.1f} days)")
    print("  → 3× RAID may be insufficient at culture-typical failure rates")
    print("  → Consider 5× minimum for deployment in radiation environments")
    print("  → Key unknown: actual neoblast migration time in engineered tissue")
    print("    (literature is in vivo; ex vivo culture may be faster or slower)")
    print("=" * 65)


if __name__ == '__main__':
    run_regeneration_analysis(n_trials=3000)
