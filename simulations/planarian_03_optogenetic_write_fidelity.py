"""
Acheron Simulation 2: Optogenetic Write Fidelity
=================================================

PURPOSE:
The encoder assumes 100% of targeted cells reach exactly the target voltage.
Real optogenetics has three sources of write error before biological noise
even enters the picture:

1. ChR2 expression variability    — cells express different amounts of opsin
2. Light attenuation in tissue    — intensity drops exponentially with depth
3. Photocurrent kinetics          — ChR2 opens/closes on ms timescale

This simulation models what pattern is ACTUALLY written to the tissue versus
what was INTENDED, giving a write fidelity percentage.

KEY QUESTION:
If 40% of cells have sub-threshold ChR2 expression, and light drops 50% by
the bottom cell layer, what fraction of cells actually reach the target voltage?

PHYSICAL MODELS:
- ChR2 expression:   log-normal distribution (μ=1.0, σ=variability_cv)
- Light attenuation: Beer-Lambert law: I(z) = I0 × exp(-μ_tissue × z)
                     μ_tissue ≈ 2.0 mm⁻¹ at 470 nm in soft tissue
- Photocurrent:      I_photo = g_ChR2 × expression × (I_light/I_sat) × (E_rev - V)
                     where g_ChR2 = peak conductance, E_rev ≈ 0 mV

OUTPUT:
- Write fidelity heatmap vs expression variability × tissue depth
- Minimum required illumination intensity for reliable writing
- Recommended cell layer thickness for the hardware design
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dataclasses import dataclass
from typing import List, Dict, Tuple
import os


# ─────────────────────────────────────────────
# Optogenetic parameters
# ─────────────────────────────────────────────

@dataclass
class OptogeneticConfig:
    """Physical parameters of the ChR2 / eNpHR3.0 optogenetic system."""

    # ChR2 (depolarization — writes "bit 1") — 470 nm blue light
    chr2_peak_conductance: float = 0.5     # nS — typical single-cell ChR2 conductance
    chr2_reversal_potential: float = 0.0   # mV — ChR2 is non-selective cation channel
    chr2_saturation_irradiance: float = 1.0  # mW/mm² — half-saturation intensity
    chr2_on_tau: float = 2.0               # ms — channel opening time constant
    chr2_off_tau: float = 10.0             # ms — channel closing time constant

    # eNpHR3.0 (hyperpolarization — writes "bit 0") — 590 nm yellow light
    nphr_peak_conductance: float = 0.3     # nS
    nphr_reversal_potential: float = -100.0  # mV — chloride reversal potential
    nphr_saturation_irradiance: float = 2.0  # mW/mm²

    # Tissue optical properties at 470 nm (blue, for ChR2)
    # μ_total = absorption + scattering coefficient for soft tissue
    # Literature: ~1.5–3.0 mm⁻¹ for 470 nm in brain/soft tissue
    tissue_attenuation_coeff: float = 2.0  # mm⁻¹

    # DMD illumination parameters
    surface_irradiance: float = 5.0        # mW/mm² at tissue surface (adjustable)
    pulse_duration_ms: float = 500.0       # ms — write pulse duration

    # Voltage targets (from base simulator)
    V_rest: float  = -50.0  # mV
    V_high: float  = -10.0  # mV  (bit 1 target)
    V_low:  float  = -80.0  # mV  (bit 0 target)


# ─────────────────────────────────────────────
# Cell model
# ─────────────────────────────────────────────

class OptogeneticCellModel:
    """
    Single-cell model of optogenetic stimulation response.

    Models the voltage trajectory of one planarian somatic cell during
    a light pulse, accounting for expression level and local light intensity.
    """

    def __init__(self,
                 expression_level: float,
                 local_irradiance: float,
                 config: OptogeneticConfig,
                 opsin_type: str = 'chr2'):
        """
        Args:
            expression_level: Normalized opsin expression (1.0 = median)
            local_irradiance: Light intensity at this cell's depth (mW/mm²)
            config:           Optogenetic system parameters
            opsin_type:       'chr2' (depolarize) or 'nphr' (hyperpolarize)
        """
        self.expression = max(0.0, expression_level)
        self.irradiance = max(0.0, local_irradiance)
        self.config     = config
        self.opsin_type = opsin_type

        self.V          = config.V_rest
        self.channel_open_prob = 0.0  # fraction of channels open

        # Parameters depending on opsin type
        if opsin_type == 'chr2':
            self.g_peak    = config.chr2_peak_conductance
            self.E_rev     = config.chr2_reversal_potential
            self.I_sat     = config.chr2_saturation_irradiance
            self.tau_on    = config.chr2_on_tau
            self.tau_off   = config.chr2_off_tau
        else:  # nphr
            self.g_peak    = config.nphr_peak_conductance
            self.E_rev     = config.nphr_reversal_potential
            self.I_sat     = config.nphr_saturation_irradiance
            self.tau_on    = 5.0    # eNpHR3.0 is slightly slower
            self.tau_off   = 20.0

        # Cell biophysics
        self.C_mem  = 10.0    # pF — small somatic cell
        self.R_mem  = 500.0   # MΩ — high resistance somatic cell
        self.V_rest = config.V_rest

    def steady_state_open_prob(self) -> float:
        """Fraction of channels open at steady state for given irradiance."""
        # Hill-type activation: P_open = I / (I + I_sat)
        return self.irradiance / (self.irradiance + self.I_sat)

    def step_ms(self, dt_ms: float, light_on: bool):
        """Advance cell voltage by dt milliseconds."""
        # Update channel open probability (first-order kinetics)
        P_target = self.steady_state_open_prob() if light_on else 0.0
        tau      = self.tau_on if (P_target > self.channel_open_prob) else self.tau_off
        dP       = (P_target - self.channel_open_prob) / tau * dt_ms
        self.channel_open_prob = np.clip(self.channel_open_prob + dP, 0.0, 1.0)

        # Photocurrent (scales with expression level and open probability)
        # Units: g_eff (nS) × ΔV (mV) = nS × mV = 10⁻⁹S × 10⁻³V = 10⁻¹²A = pA
        g_eff    = self.g_peak * self.expression * self.channel_open_prob
        I_photo  = g_eff * (self.E_rev - self.V)   # pA — no conversion needed

        # Leak current back toward rest
        # Units: ΔV (mV) / R (MΩ) = 10⁻³V / 10⁶Ω = 10⁻⁹A = nA → × 1000 = pA
        I_leak   = (self.V_rest - self.V) / self.R_mem * 1000  # pA

        # Total current → voltage change
        # dV/dt = I_total / C_mem  [pA / pF = mV/ms]
        I_total  = I_photo + I_leak
        dV       = (I_total / self.C_mem) * dt_ms
        self.V   = np.clip(self.V + dV, -120.0, 60.0)

    def simulate_pulse(self, pulse_duration_ms: float,
                       dt_ms: float = 0.5) -> float:
        """
        Simulate a write pulse and return final voltage.

        Returns:
            Voltage (mV) after pulse_duration_ms of illumination
        """
        self.V = self.V_rest
        self.channel_open_prob = 0.0
        n_steps = int(pulse_duration_ms / dt_ms)
        for _ in range(n_steps):
            self.step_ms(dt_ms, light_on=True)
        return self.V


# ─────────────────────────────────────────────
# Write fidelity analysis
# ─────────────────────────────────────────────

class WriteFidelityAnalyzer:
    """
    Analyzes write fidelity across a population of cells with realistic
    variability in expression level and tissue depth.
    """

    def __init__(self, config: OptogeneticConfig = None):
        self.config = config or OptogeneticConfig()

    def _sample_expression_levels(self,
                                   n_cells: int,
                                   cv: float,
                                   seed: int = 0) -> np.ndarray:
        """
        Sample ChR2 expression levels from log-normal distribution.

        CV (coefficient of variation) = std / mean
        Literature: 30–70% CV in transiently transfected cell populations.
        Stable cell lines: 15–30% CV.
        """
        np.random.seed(seed)
        if cv <= 0:
            return np.ones(n_cells)
        sigma = np.sqrt(np.log(1 + cv**2))
        mu    = -0.5 * sigma**2   # ensures median ≈ 1.0
        return np.random.lognormal(mu, sigma, n_cells)

    def _beer_lambert_intensity(self, surface_irradiance: float,
                                 depth_mm: float) -> float:
        """I(z) = I0 × exp(-μ × z)"""
        return surface_irradiance * np.exp(
            -self.config.tissue_attenuation_coeff * depth_mm)

    def analyze_tile(self,
                     n_cells: int = 9,
                     tissue_thickness_mm: float = 0.1,
                     expression_cv: float = 0.25,
                     opsin_type: str = 'chr2',
                     seed: int = 42) -> Dict:
        """
        Simulate writing to one tile of n_cells with realistic variability.

        Args:
            n_cells:              Cells in the tile
            tissue_thickness_mm:  Total tissue depth (cells distributed evenly)
            expression_cv:        Coefficient of variation for expression level
            opsin_type:           'chr2' or 'nphr'
            seed:                 Random seed

        Returns:
            Dictionary with fidelity metrics
        """
        # Distribute cells evenly through tissue depth
        depths = np.linspace(0, tissue_thickness_mm, n_cells)

        # Sample expression levels
        expressions = self._sample_expression_levels(n_cells, expression_cv, seed)

        # Simulate each cell
        final_voltages = []
        for depth, expr in zip(depths, expressions):
            local_irr = self._beer_lambert_intensity(
                self.config.surface_irradiance, depth)
            cell = OptogeneticCellModel(expr, local_irr, self.config, opsin_type)
            v_final = cell.simulate_pulse(self.config.pulse_duration_ms)
            final_voltages.append(v_final)

        final_voltages = np.array(final_voltages)

        # Fidelity: fraction of cells that reached at least 70% of target displacement
        target_V = self.config.V_high if opsin_type == 'chr2' else self.config.V_low
        displacement_needed = abs(target_V - self.config.V_rest) * 0.70

        if opsin_type == 'chr2':
            success = final_voltages >= (self.config.V_rest + displacement_needed)
        else:
            success = final_voltages <= (self.config.V_rest - displacement_needed)

        fidelity  = success.mean()
        mean_V    = final_voltages.mean()
        std_V     = final_voltages.std()
        # Majority vote: does the cluster correctly classify as intended bit?
        midpoint  = (self.config.V_high + self.config.V_low) / 2.0
        if opsin_type == 'chr2':
            majority = 1 if mean_V > midpoint else 0
        else:
            majority = 0 if mean_V < midpoint else 1
        expected = 1 if opsin_type == 'chr2' else 0

        return {
            'fidelity':      fidelity,
            'mean_voltage':  mean_V,
            'std_voltage':   std_V,
            'target_voltage': target_V,
            'majority_correct': majority == expected,
            'voltages':       final_voltages,
            'expressions':    expressions,
            'depths':         depths,
        }

    def sweep_expression_vs_depth(self,
                                   cv_values: List[float],
                                   thickness_values: List[float],
                                   opsin_type: str = 'chr2',
                                   n_seeds: int = 10) -> np.ndarray:
        """
        2D sweep: expression variability (CV) × tissue thickness.

        Returns fidelity matrix of shape (len(cv_values), len(thickness_values)).
        """
        fidelity_matrix = np.zeros((len(cv_values), len(thickness_values)))
        majority_matrix = np.zeros_like(fidelity_matrix)

        for i, cv in enumerate(cv_values):
            for j, thickness in enumerate(thickness_values):
                # Average over multiple seeds
                fids, majorities = [], []
                for seed in range(n_seeds):
                    result = self.analyze_tile(
                        n_cells=9,
                        tissue_thickness_mm=thickness,
                        expression_cv=cv,
                        opsin_type=opsin_type,
                        seed=seed,
                    )
                    fids.append(result['fidelity'])
                    majorities.append(float(result['majority_correct']))
                fidelity_matrix[i, j] = np.mean(fids)
                majority_matrix[i, j] = np.mean(majorities)

        return fidelity_matrix, majority_matrix

    def analyze_irradiance_requirement(self,
                                        depth_mm: float = 0.2,
                                        expression_cv: float = 0.25,
                                        irradiance_values: List[float] = None,
                                        n_seeds: int = 20) -> Dict:
        """Find minimum surface irradiance for reliable writing at given depth."""
        if irradiance_values is None:
            irradiance_values = np.linspace(0.5, 20.0, 30).tolist()

        results_chr2 = []
        results_nphr = []
        original_irr = self.config.surface_irradiance

        for irr in irradiance_values:
            self.config.surface_irradiance = irr
            fids_chr2, fids_nphr = [], []
            for seed in range(n_seeds):
                r1 = self.analyze_tile(tissue_thickness_mm=depth_mm,
                                       expression_cv=expression_cv,
                                       opsin_type='chr2', seed=seed)
                r2 = self.analyze_tile(tissue_thickness_mm=depth_mm,
                                       expression_cv=expression_cv,
                                       opsin_type='nphr', seed=seed)
                fids_chr2.append(r1['fidelity'])
                fids_nphr.append(r2['fidelity'])
            results_chr2.append(np.mean(fids_chr2))
            results_nphr.append(np.mean(fids_nphr))

        self.config.surface_irradiance = original_irr
        return {
            'irradiance_values': irradiance_values,
            'chr2_fidelity':     results_chr2,
            'nphr_fidelity':     results_nphr,
        }


# ─────────────────────────────────────────────
# Plotting and reporting
# ─────────────────────────────────────────────

def run_write_fidelity_analysis(output_dir: str = 'analysis'):
    """Run the full write fidelity analysis and generate diagnostic plots."""
    os.makedirs(output_dir, exist_ok=True)

    config   = OptogeneticConfig()
    analyzer = WriteFidelityAnalyzer(config)

    print("=" * 65)
    print("ACHERON OPTOGENETIC WRITE FIDELITY ANALYZER")
    print("=" * 65)

    # ── Sweep 1: Expression variability × tissue depth ─────────────────
    print("\nRunning sweep: expression CV × tissue depth ...")
    cv_values        = [0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60]
    thickness_values = [0.05, 0.10, 0.20, 0.30, 0.50, 0.75, 1.0]  # mm

    fid_chr2, maj_chr2 = analyzer.sweep_expression_vs_depth(
        cv_values, thickness_values, opsin_type='chr2', n_seeds=15)
    fid_nphr, maj_nphr = analyzer.sweep_expression_vs_depth(
        cv_values, thickness_values, opsin_type='nphr', n_seeds=15)

    # ── Sweep 2: Required irradiance vs depth ──────────────────────────
    print("Running sweep: irradiance requirement ...")
    irr_results = analyzer.analyze_irradiance_requirement(
        depth_mm=0.20, expression_cv=0.25)

    # ── Single tile detailed view ──────────────────────────────────────
    print("Running single-tile detailed view ...")
    tile_ideal    = analyzer.analyze_tile(expression_cv=0.0,   seed=0)
    tile_mild     = analyzer.analyze_tile(expression_cv=0.25,  seed=0)
    tile_severe   = analyzer.analyze_tile(expression_cv=0.50,  seed=0)

    # ── Plotting ───────────────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 14))
    fig.suptitle("Acheron Optogenetic Write Fidelity Analysis\n"
                 "What does the tissue actually receive vs. what was intended?",
                 fontsize=13, fontweight='bold')

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.40)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])
    ax4 = fig.add_subplot(gs[1, 0])
    ax5 = fig.add_subplot(gs[1, 1])
    ax6 = fig.add_subplot(gs[1, 2])

    cv_labels        = [f'{v:.0%}' for v in cv_values]
    thickness_labels = [f'{v*1000:.0f}μm' for v in thickness_values]

    # Panel 1: ChR2 fidelity heatmap
    im1 = ax1.imshow(fid_chr2, aspect='auto', cmap='RdYlGn',
                     vmin=0.5, vmax=1.0, origin='lower')
    ax1.set_xticks(range(len(thickness_values)))
    ax1.set_xticklabels(thickness_labels, rotation=45, fontsize=8)
    ax1.set_yticks(range(len(cv_values)))
    ax1.set_yticklabels(cv_labels, fontsize=8)
    ax1.set_xlabel('Tissue Depth')
    ax1.set_ylabel('Expression Variability (CV)')
    ax1.set_title('ChR2 Write Fidelity\n(Bit 1 — Blue 470nm)')
    plt.colorbar(im1, ax=ax1, label='Fidelity')
    for i in range(len(cv_values)):
        for j in range(len(thickness_values)):
            ax1.text(j, i, f'{fid_chr2[i,j]:.0%}',
                    ha='center', va='center', fontsize=7,
                    color='black' if fid_chr2[i,j] > 0.7 else 'white')

    # Panel 2: eNpHR3.0 fidelity heatmap
    im2 = ax2.imshow(fid_nphr, aspect='auto', cmap='RdYlGn',
                     vmin=0.5, vmax=1.0, origin='lower')
    ax2.set_xticks(range(len(thickness_values)))
    ax2.set_xticklabels(thickness_labels, rotation=45, fontsize=8)
    ax2.set_yticks(range(len(cv_values)))
    ax2.set_yticklabels(cv_labels, fontsize=8)
    ax2.set_xlabel('Tissue Depth')
    ax2.set_ylabel('Expression Variability (CV)')
    ax2.set_title('eNpHR3.0 Write Fidelity\n(Bit 0 — Yellow 590nm)')
    plt.colorbar(im2, ax=ax2, label='Fidelity')
    for i in range(len(cv_values)):
        for j in range(len(thickness_values)):
            ax2.text(j, i, f'{fid_nphr[i,j]:.0%}',
                    ha='center', va='center', fontsize=7,
                    color='black' if fid_nphr[i,j] > 0.7 else 'white')

    # Panel 3: Irradiance requirement
    irr_vals = irr_results['irradiance_values']
    ax3.plot(irr_vals, irr_results['chr2_fidelity'], 'b-o',
             linewidth=2, markersize=4, label='ChR2 (blue 470nm)')
    ax3.plot(irr_vals, irr_results['nphr_fidelity'], 'y-s',
             linewidth=2, markersize=4, label='eNpHR3.0 (yellow 590nm)',
             color='orange')
    ax3.axhline(0.80, color='black', linestyle='--', label='80% fidelity target')
    ax3.axvline(config.surface_irradiance, color='red', linestyle=':',
                label=f'Current setting ({config.surface_irradiance} mW/mm²)')
    ax3.set_xlabel('Surface Irradiance (mW/mm²)')
    ax3.set_ylabel('Write Fidelity')
    ax3.set_title(f'Required Irradiance\nat depth={config.tissue_attenuation_coeff}mm⁻¹, '
                  f'CV=25%, d=0.2mm')
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # Panel 4: Single-cell voltage profiles
    n = len(tile_ideal['voltages'])
    ax4.bar(range(n), tile_ideal['voltages'],
            color='green', alpha=0.7, label=f'CV=0% (ideal)')
    ax4.bar(range(n), tile_mild['voltages'],
            color='blue', alpha=0.5, label=f'CV=25%')
    ax4.bar(range(n), tile_severe['voltages'],
            color='red', alpha=0.4, label=f'CV=50%')
    ax4.axhline(config.V_high, color='green', linestyle='--', linewidth=1.5,
                label=f'Target V_high ({config.V_high}mV)')
    ax4.axhline((config.V_high + config.V_rest)/2, color='gray', linestyle=':',
                label='50% displacement')
    ax4.set_xlabel('Cell Index (depth increases →)')
    ax4.set_ylabel('Post-pulse Voltage (mV)')
    ax4.set_title('Per-Cell Voltage After ChR2 Write Pulse\n(9-cell tile)')
    ax4.legend(fontsize=8)
    ax4.grid(True, alpha=0.3)

    # Panel 5: Expression distribution comparison
    cv_plot_list = [0.10, 0.25, 0.40, 0.60]
    colors       = ['green', 'blue', 'orange', 'red']
    np.random.seed(99)
    for cv_p, col in zip(cv_plot_list, colors):
        if cv_p <= 0:
            continue
        sigma = np.sqrt(np.log(1 + cv_p**2))
        mu    = -0.5 * sigma**2
        samples = np.random.lognormal(mu, sigma, 1000)
        ax5.hist(samples, bins=50, alpha=0.5, color=col, density=True,
                 label=f'CV={cv_p:.0%}')
    ax5.axvline(1.0, color='black', linestyle='--', linewidth=2,
                label='Median expression (1.0)')
    ax5.axvline(0.3, color='gray', linestyle=':', linewidth=1.5,
                label='Functional threshold (~0.3)')
    ax5.set_xlabel('Normalized ChR2 Expression Level')
    ax5.set_ylabel('Density')
    ax5.set_title('Expression Level Distribution\n(Log-normal model)')
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)
    ax5.set_xlim(0, 4)

    # Panel 6: Light attenuation profile
    depths_plot = np.linspace(0, 1.5, 200)
    for irr0, ls in [(1.0, '--'), (5.0, '-'), (10.0, '-.')]:
        intensities = irr0 * np.exp(-config.tissue_attenuation_coeff * depths_plot)
        ax6.plot(intensities, depths_plot * 1000,
                 linestyle=ls, linewidth=2,
                 label=f'Surface: {irr0} mW/mm²')
    ax6.axvline(config.chr2_saturation_irradiance, color='blue',
                linestyle=':', linewidth=2,
                label=f'ChR2 I_sat ({config.chr2_saturation_irradiance} mW/mm²)')
    ax6.set_xlabel('Local Irradiance (mW/mm²)')
    ax6.set_ylabel('Tissue Depth (μm)')
    ax6.set_title(f'Light Attenuation in Tissue\n'
                  f'Beer-Lambert: μ={config.tissue_attenuation_coeff} mm⁻¹ at 470nm')
    ax6.legend(fontsize=8)
    ax6.grid(True, alpha=0.3)
    ax6.invert_yaxis()

    path = os.path.join(output_dir, 'write_fidelity_analysis.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {path}")
    plt.close(fig)

    # ── Summary ────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print("WRITE FIDELITY ANALYSIS — SUMMARY")
    print("=" * 65)
    print(f"Configuration: surface irradiance={config.surface_irradiance} mW/mm²,")
    print(f"               attenuation={config.tissue_attenuation_coeff} mm⁻¹,")
    print(f"               pulse={config.pulse_duration_ms} ms")
    print()
    print(f"{'Scenario':<25} {'ChR2 Fidelity':>14} {'eNpHR Fidelity':>15}")
    print("-" * 55)
    for label, cv in [("Ideal (CV=0%)", 0.0),
                      ("Mild (CV=25%)", 0.25),
                      ("Severe (CV=50%)", 0.50)]:
        r1 = analyzer.analyze_tile(expression_cv=cv, opsin_type='chr2', seed=0)
        r2 = analyzer.analyze_tile(expression_cv=cv, opsin_type='nphr', seed=0)
        print(f"{label:<25} {r1['fidelity']:>13.1%} {r2['fidelity']:>14.1%}")

    print()
    print("DESIGN IMPLICATIONS:")
    print("  → If CV > 30%: stable cell lines required (not transient transfection)")
    print("  → Tissue depth must stay < 300 μm for reliable ChR2 activation")
    print("  → Minimum surface irradiance: find crossover at 80% fidelity in panel 3")
    print("  → Key measurement needed: characterize ChR2 expression CV in planarian")
    print("    somatic cells after transfection (flow cytometry or single-cell qPCR)")
    print("=" * 65)


if __name__ == '__main__':
    run_write_fidelity_analysis()
