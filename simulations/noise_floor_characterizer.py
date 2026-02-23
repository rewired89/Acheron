"""
Acheron Simulation 1: Biological Noise Floor Characterizer
===========================================================

PURPOSE:
The existing persistence simulator assumes perfect biology — zero noise,
uniform cell properties, deterministic ion channel behavior. Real planarian
tissue has four major noise sources that will degrade pattern integrity.
This simulation injects realistic noise and finds the breaking point.

NOISE SOURCES MODELED:
1. Ion channel shot noise    — stochastic channel opening/closing (±5–8 mV)
2. Cell-to-cell variability  — 20–50% variation in R_mem and g_gap across cells
3. Metabolic noise           — ATP fluctuation drives pump activity variation
4. Thermal noise             — Johnson-Nyquist at biological temperature

KEY QUESTION:
At what combined noise level does the 70 mV signal separation become
unreadable within 24 hours? This is the go/no-go threshold for the
entire bioelectric storage concept.

OUTPUT:
- SNR vs pattern integrity curve over 24 hours
- Breaking point: minimum noise level that causes >30% integrity loss
- Recommended experimental noise floor measurement targets
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
import time
import os


# ─────────────────────────────────────────────
# Noise configuration
# ─────────────────────────────────────────────

@dataclass
class NoiseProfile:
    """
    Defines a biological noise scenario to test.

    All values derived from electrophysiology literature on small somatic
    cells (~10–50 pF capacitance, ~100–500 MΩ input resistance).
    """
    name: str

    # Ion channel shot noise: std dev of per-cell per-step voltage fluctuation (mV)
    # Source: single-channel recordings in epithelial cells
    # Range: 0 mV (ideal) → 5 mV (mild) → 10 mV (realistic) → 20 mV (severe)
    channel_noise_std: float = 0.0

    # Cell-to-cell variability: fraction of R_mem and g_gap that varies per cell
    # Source: patch-clamp surveys showing 20–50% coefficient of variation
    # Range: 0.0 (ideal) → 0.2 (mild) → 0.4 (realistic) → 0.6 (severe)
    cell_variability_cv: float = 0.0

    # Metabolic noise: fraction of membrane current that fluctuates randomly
    # Source: ATP depletion studies in epithelial ion pumps
    # Range: 0.0 (ideal) → 0.05 (mild) → 0.15 (realistic) → 0.30 (severe)
    metabolic_noise_fraction: float = 0.0

    # Thermal noise: Johnson-Nyquist contribution (mV)
    # Calculated: sqrt(4 * k_B * T * R * BW) at 20°C, R=200MΩ, BW=0.1Hz ≈ 0.4 mV
    # This is always present; set to 0 only for baseline comparison
    thermal_noise_std: float = 0.0


# Noise scenarios from idealized to realistic
NOISE_PROFILES = [
    NoiseProfile("Ideal (simulation baseline)",
                 channel_noise_std=0.0, cell_variability_cv=0.0,
                 metabolic_noise_fraction=0.0, thermal_noise_std=0.0),

    NoiseProfile("Mild biological noise",
                 channel_noise_std=2.0, cell_variability_cv=0.10,
                 metabolic_noise_fraction=0.03, thermal_noise_std=0.4),

    NoiseProfile("Realistic biological noise",
                 channel_noise_std=5.0, cell_variability_cv=0.25,
                 metabolic_noise_fraction=0.10, thermal_noise_std=0.4),

    NoiseProfile("Severe biological noise",
                 channel_noise_std=10.0, cell_variability_cv=0.40,
                 metabolic_noise_fraction=0.20, thermal_noise_std=0.4),

    NoiseProfile("Worst case",
                 channel_noise_std=15.0, cell_variability_cv=0.50,
                 metabolic_noise_fraction=0.30, thermal_noise_std=0.4),
]


# ─────────────────────────────────────────────
# Noisy tissue model
# ─────────────────────────────────────────────

class NoisyPlanarianTissue:
    """
    Planarian tissue model with biological noise injection.

    Extends the base PlanarianTissueModel by:
    1. Giving each cell individual R_mem and g_gap drawn from distributions
    2. Adding per-step stochastic voltage fluctuations
    3. Modeling metabolic noise as pump current variability
    4. Adding thermal (Johnson-Nyquist) noise floor
    """

    # Base parameters (from optimized persistence simulator)
    V_REST  = -50.0   # mV
    V_HIGH  = -10.0   # mV  ("bit 1")
    V_LOW   = -80.0   # mV  ("bit 0")
    G_GAP   = 0.005   # nS  (base gap junction conductance)
    R_MEM   = 200.0   # MΩ  (base membrane resistance)
    TAU     = 240.0   # min (relaxation time constant)
    C_MEM   = 5.0     # μF/cm²

    # Cell cluster size for each bit (3×3 = 9 cells per bit)
    CLUSTER_SIZE = 3

    def __init__(self,
                 grid_size: Tuple[int, int] = (30, 30),
                 dt: float = 0.5,
                 noise: NoiseProfile = None,
                 seed: int = None):
        """
        Args:
            grid_size: (rows, cols) of tissue
            dt:        timestep in minutes
            noise:     NoiseProfile to apply
            seed:      random seed for reproducibility
        """
        if seed is not None:
            np.random.seed(seed)

        self.rows, self.cols = grid_size
        self.dt = dt
        self.noise = noise or NoiseProfile("Ideal")
        self.time = 0.0

        # Voltage grid
        self.V = np.full((self.rows, self.cols), self.V_REST)

        # Per-cell membrane resistance — sampled from log-normal distribution
        # Log-normal keeps values positive and matches biological heterogeneity
        if self.noise.cell_variability_cv > 0:
            sigma_lognorm = np.sqrt(np.log(1 + self.noise.cell_variability_cv**2))
            mu_lognorm    = np.log(self.R_MEM) - 0.5 * sigma_lognorm**2
            self.R_mem_grid = np.random.lognormal(mu_lognorm, sigma_lognorm,
                                                   (self.rows, self.cols))
            # Per-cell gap junction conductance
            mu_g    = np.log(self.G_GAP) - 0.5 * sigma_lognorm**2
            self.g_gap_grid = np.random.lognormal(mu_g, sigma_lognorm,
                                                   (self.rows, self.cols))
        else:
            self.R_mem_grid  = np.full((self.rows, self.cols), self.R_MEM)
            self.g_gap_grid  = np.full((self.rows, self.cols), self.G_GAP)

        # Track integrity history
        self.history: List[Dict] = []
        self._bit_regions: List[Tuple[List, int]] = []  # (coords, bit_value)

    def write_bit(self, row_center: int, col_center: int, bit_value: int):
        """Write a single bit to a CLUSTER_SIZE × CLUSTER_SIZE cell cluster."""
        half = self.CLUSTER_SIZE // 2
        coords = []
        for r in range(row_center - half, row_center + half + 1):
            for c in range(col_center - half, col_center + half + 1):
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    self.V[r, c] = self.V_HIGH if bit_value else self.V_LOW
                    coords.append((r, c))
        self._bit_regions.append((coords, bit_value))

    def _gap_current(self) -> np.ndarray:
        """Gap junction currents with per-cell conductance."""
        I = np.zeros_like(self.V)
        g = self.g_gap_grid
        # Average conductance at each junction = mean of two neighboring cells
        I[1:,  :] += 0.5*(g[1:,  :]+g[:-1, :]) * (self.V[:-1, :] - self.V[1:,  :])
        I[:-1, :] += 0.5*(g[:-1, :]+g[1:,  :]) * (self.V[1:,  :] - self.V[:-1, :])
        I[:,  1:] += 0.5*(g[:,  1:]+g[:, :-1]) * (self.V[:, :-1] - self.V[:,  1:])
        I[:, :-1] += 0.5*(g[:, :-1]+g[:,  1:]) * (self.V[:,  1:] - self.V[:, :-1])
        return I

    def _membrane_current(self) -> np.ndarray:
        """Leak current toward rest, with per-cell R_mem and metabolic noise."""
        I_base = (self.V_REST - self.V) / (self.R_mem_grid * self.TAU)
        if self.noise.metabolic_noise_fraction > 0:
            # Pump activity fluctuates as a fraction of the base current
            noise_amplitude = np.abs(I_base) * self.noise.metabolic_noise_fraction
            I_base += np.random.normal(0, noise_amplitude,
                                       (self.rows, self.cols))
        return I_base

    def step(self):
        """Advance one timestep with all noise sources applied."""
        I_gap = self._gap_current()
        I_mem = self._membrane_current()

        dV = (I_gap + I_mem) / self.C_MEM * self.dt

        # Ion channel shot noise (additive Gaussian, per cell per step)
        if self.noise.channel_noise_std > 0:
            dV += np.random.normal(0,
                                   self.noise.channel_noise_std * np.sqrt(self.dt),
                                   (self.rows, self.cols))

        # Thermal (Johnson-Nyquist) noise
        if self.noise.thermal_noise_std > 0:
            dV += np.random.normal(0,
                                   self.noise.thermal_noise_std * np.sqrt(self.dt),
                                   (self.rows, self.cols))

        self.V += dV
        # Clamp to physiologically plausible range
        np.clip(self.V, -120.0, 60.0, out=self.V)
        self.time += self.dt

        if int(self.time) % 30 == 0:
            self.history.append({
                'time_hr': self.time / 60.0,
                'integrity': self._measure_integrity(),
                'snr':       self._measure_snr(),
            })

    def _measure_integrity(self) -> float:
        """
        Fraction of bit-cluster cells still correctly classified.

        A cell is correct if its voltage is closer to its target state
        than to the opposite state.
        """
        if not self._bit_regions:
            return 1.0
        correct = 0
        total   = 0
        midpoint = (self.V_HIGH + self.V_LOW) / 2.0  # -45 mV
        for coords, bit_value in self._bit_regions:
            for (r, c) in coords:
                v = self.V[r, c]
                predicted = 1 if v > midpoint else 0
                correct  += int(predicted == bit_value)
                total    += 1
        return correct / total if total > 0 else 0.0

    def _measure_snr(self) -> float:
        """
        Signal-to-noise ratio: mean separation / std deviation within clusters.

        SNR = (mean(V_bit1_cells) - mean(V_bit0_cells)) / pooled_std
        """
        v1_vals, v0_vals = [], []
        for coords, bit_value in self._bit_regions:
            for (r, c) in coords:
                (v1_vals if bit_value == 1 else v0_vals).append(self.V[r, c])
        if not v1_vals or not v0_vals:
            return 0.0
        v1 = np.array(v1_vals)
        v0 = np.array(v0_vals)
        separation = np.mean(v1) - np.mean(v0)
        pooled_std = np.sqrt((np.var(v1) + np.var(v0)) / 2.0) + 1e-9
        return float(separation / pooled_std)

    def run(self, duration_hours: float = 24.0) -> Dict:
        """Run simulation and return final metrics."""
        n_steps = int(duration_hours * 60 / self.dt)
        for _ in range(n_steps):
            self.step()
        return {
            'final_integrity': self._measure_integrity(),
            'final_snr':       self._measure_snr(),
            'history':         self.history,
        }


# ─────────────────────────────────────────────
# Multi-bit test pattern
# ─────────────────────────────────────────────

def setup_test_pattern(tissue: NoisyPlanarianTissue):
    """Write alternating 1/0 pattern across the tissue for maximum stress test."""
    bits = [1, 0, 1, 0, 1, 0]
    spacing = tissue.cols // (len(bits) + 1)
    row_center = tissue.rows // 2
    for i, bit in enumerate(bits):
        col_center = spacing * (i + 1)
        tissue.write_bit(row_center, col_center, bit)


# ─────────────────────────────────────────────
# Main analysis
# ─────────────────────────────────────────────

def run_noise_sweep(duration_hours: float = 24.0,
                    n_seeds: int = 5,
                    output_dir: str = 'analysis') -> Dict:
    """
    Run all noise profiles and collect integrity + SNR data.

    Args:
        duration_hours: Simulation duration
        n_seeds:        Number of random seeds per profile (for averaging)
        output_dir:     Directory for output plots
    """
    os.makedirs(output_dir, exist_ok=True)
    results = {}

    print("=" * 65)
    print("ACHERON NOISE FLOOR CHARACTERIZER")
    print("=" * 65)
    print(f"Duration: {duration_hours}h | Seeds per profile: {n_seeds}")
    print()

    for profile in NOISE_PROFILES:
        print(f"Running: {profile.name} ...")
        t0 = time.time()

        seed_results = []
        for seed in range(n_seeds):
            tissue = NoisyPlanarianTissue(grid_size=(30, 30), dt=0.5,
                                          noise=profile, seed=seed * 100)
            setup_test_pattern(tissue)
            r = tissue.run(duration_hours)
            seed_results.append(r)

        # Aggregate across seeds
        # Align histories by time index
        min_len = min(len(r['history']) for r in seed_results)
        times   = [h['time_hr'] for h in seed_results[0]['history'][:min_len]]

        integrity_matrix = np.array([
            [h['integrity'] for h in r['history'][:min_len]]
            for r in seed_results
        ])
        snr_matrix = np.array([
            [h['snr'] for h in r['history'][:min_len]]
            for r in seed_results
        ])

        results[profile.name] = {
            'profile':            profile,
            'times':              times,
            'integrity_mean':     integrity_matrix.mean(axis=0),
            'integrity_std':      integrity_matrix.std(axis=0),
            'snr_mean':           snr_matrix.mean(axis=0),
            'snr_std':            snr_matrix.std(axis=0),
            'final_integrity':    np.mean([r['final_integrity'] for r in seed_results]),
            'final_snr':          np.mean([r['final_snr']       for r in seed_results]),
        }

        print(f"  Final integrity: {results[profile.name]['final_integrity']:.1%} | "
              f"Final SNR: {results[profile.name]['final_snr']:.1f}:1 | "
              f"({time.time()-t0:.1f}s)")

    _plot_results(results, duration_hours, output_dir)
    _print_summary(results)
    return results


def _plot_results(results: Dict, duration_hours: float, output_dir: str):
    """Generate the three-panel diagnostic plot."""
    fig = plt.figure(figsize=(16, 14))
    fig.suptitle("Acheron Noise Floor Analysis\n"
                 "Does the storage medium survive contact with real biology?",
                 fontsize=14, fontweight='bold', y=0.98)

    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.40, wspace=0.35)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])

    colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#8e44ad']
    threshold = 0.70  # 70% integrity = minimum acceptable

    # ── Panel 1: Integrity over time ──────────────────────────────────
    for (name, data), color in zip(results.items(), colors):
        t   = data['times']
        mu  = data['integrity_mean']
        sig = data['integrity_std']
        ax1.plot(t, mu, color=color, linewidth=2, label=name)
        ax1.fill_between(t, mu - sig, mu + sig, color=color, alpha=0.15)

    ax1.axhline(threshold, color='black', linestyle='--', linewidth=1.5,
                label=f'Threshold ({threshold:.0%})')
    ax1.set_xlabel('Time (hours)')
    ax1.set_ylabel('Bit Integrity (fraction correct)')
    ax1.set_title('Pattern Integrity Over Time\nby Noise Level')
    ax1.set_ylim(0, 1.05)
    ax1.legend(fontsize=7, loc='lower left')
    ax1.grid(True, alpha=0.3)

    # ── Panel 2: SNR over time ─────────────────────────────────────────
    for (name, data), color in zip(results.items(), colors):
        t   = data['times']
        mu  = data['snr_mean']
        sig = data['snr_std']
        ax2.plot(t, mu, color=color, linewidth=2, label=name)
        ax2.fill_between(t, np.maximum(mu - sig, 0), mu + sig,
                         color=color, alpha=0.15)

    ax2.axhline(3.0, color='black', linestyle='--', linewidth=1.5,
                label='Minimum reliable SNR (3:1)')
    ax2.set_xlabel('Time (hours)')
    ax2.set_ylabel('SNR (signal / noise)')
    ax2.set_title('Signal-to-Noise Ratio Over Time\nby Noise Level')
    ax2.legend(fontsize=7, loc='upper right')
    ax2.grid(True, alpha=0.3)

    # ── Panel 3: Final integrity bar chart ────────────────────────────
    names           = list(results.keys())
    final_integrity = [results[n]['final_integrity'] for n in names]
    final_snr       = [results[n]['final_snr']       for n in names]

    x   = np.arange(len(names))
    w   = 0.35
    bar_colors = [('#2ecc71' if fi >= threshold else '#e74c3c')
                  for fi in final_integrity]

    bars = ax3.bar(x - w/2, final_integrity, w, color=bar_colors,
                   alpha=0.85, label='Final Integrity')
    ax3_twin = ax3.twinx()
    ax3_twin.bar(x + w/2, final_snr, w, color='steelblue',
                 alpha=0.6, label='Final SNR')

    ax3.axhline(threshold, color='black', linestyle='--', linewidth=1.5)
    ax3.set_xticks(x)
    ax3.set_xticklabels([n.replace(' (', '\n(') for n in names], fontsize=9)
    ax3.set_ylabel('Final Integrity After 24h', color='black')
    ax3_twin.set_ylabel('Final SNR', color='steelblue')
    ax3.set_title(f'Final State After {duration_hours}h — Green = Pass, Red = Fail')
    ax3.set_ylim(0, 1.1)
    ax3.grid(True, alpha=0.3, axis='y')

    # Value labels on bars
    for bar, val in zip(bars, final_integrity):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                 f'{val:.1%}', ha='center', va='bottom', fontsize=9,
                 fontweight='bold')

    fig.legend(loc='lower right', bbox_to_anchor=(0.98, 0.02), fontsize=9)
    path = os.path.join(output_dir, 'noise_floor_analysis.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {path}")
    plt.close(fig)


def _print_summary(results: Dict):
    """Print go/no-go assessment."""
    threshold = 0.70
    snr_min   = 3.0

    print()
    print("=" * 65)
    print("NOISE FLOOR ANALYSIS — SUMMARY")
    print("=" * 65)
    print(f"{'Scenario':<40} {'Integrity':>10} {'SNR':>8} {'Status':>8}")
    print("-" * 65)

    for name, data in results.items():
        fi  = data['final_integrity']
        snr = data['final_snr']
        ok  = fi >= threshold and snr >= snr_min
        status = "PASS" if ok else "FAIL"
        print(f"{name:<40} {fi:>9.1%} {snr:>7.1f} {status:>8}")

    print()
    print("INTERPRETATION:")
    print(f"  Threshold: >{threshold:.0%} integrity AND >{snr_min:.0f}:1 SNR after 24h")
    print()
    print("  If REALISTIC NOISE fails: the storage medium cannot hold data reliably.")
    print("  Lab experiment must measure actual noise floor BEFORE building hardware.")
    print()
    print("  Key measurement needed in first wetware experiment:")
    print("  → Patch-clamp 20+ planarian somatic cells, measure Vmem over 30 min")
    print("  → Calculate actual σ_noise to validate which scenario matches reality")
    print("=" * 65)


if __name__ == '__main__':
    run_noise_sweep(duration_hours=24.0, n_seeds=5)
