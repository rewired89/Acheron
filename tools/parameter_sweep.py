"""
Acheron Parameter Sweep Optimization
=====================================

Systematically test different parameter combinations to find optimal settings
for maximum pattern persistence.

Parameters to optimize:
- Gap junction conductance (g_gap)
- Membrane resistance (R_mem)
- Relaxation time constant (tau_relax)
- Cells per bit (redundancy)

This finds the "sweet spot" where:
1. Patterns persist longest
2. Bits remain distinguishable
3. Crosstalk is minimized

Results used for:
- Patent claims (demonstrated optimization)
- Grant applications (scientific rigor)
- Product specs (engineering parameters)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from simulations.planarian_01_bioelectric_persistence import PlanarianTissueModel
import pandas as pd
from itertools import product
import time
from tqdm import tqdm


class ParameterSweep:
    """
    Systematic parameter space exploration.
    """

    def __init__(self):
        self.results = []

    def test_single_configuration(self, g_gap, R_mem, tau_relax, duration_hours=24):
        """
        Test a single parameter configuration.

        Returns:
            dict with metrics
        """
        # Create tissue with these parameters
        tissue = PlanarianTissueModel(grid_size=(30, 30), dt=1.0)  # Smaller grid for speed
        tissue.g_gap = g_gap
        tissue.R_mem = R_mem
        tissue.tau_relax = tau_relax

        # Write a test bit pattern (single 5x5 cluster)
        bit_coords = [(r, c) for r in range(12, 18) for c in range(12, 18)]
        tissue.set_bit_pattern(bit_coords, bit_value=1)

        # Record initial state
        initial_integrity = tissue.measure_bit_integrity()

        # Run simulation
        tissue.run_persistence_test(duration_hours=duration_hours)

        # Record final state
        final_integrity = tissue.measure_bit_integrity()

        # Calculate metrics
        persistence_ratio = final_integrity['integrity_ratio']
        voltage_separation = final_integrity['V_range']

        return {
            'g_gap': g_gap,
            'R_mem': R_mem,
            'tau_relax': tau_relax,
            'persistence_ratio': persistence_ratio,
            'voltage_separation': voltage_separation,
            'initial_range': initial_integrity['V_range'],
            'final_range': final_integrity['V_range'],
            'decay_rate': (initial_integrity['V_range'] - final_integrity['V_range']) / duration_hours
        }

    def sweep_gap_junction(self, g_gap_values=None):
        """
        Sweep gap junction conductance.
        """
        if g_gap_values is None:
            g_gap_values = np.logspace(-3, -1, 10)  # 0.001 to 0.1 nS

        print("\n" + "="*70)
        print("GAP JUNCTION CONDUCTANCE SWEEP")
        print("="*70 + "\n")

        print(f"Testing {len(g_gap_values)} values...")
        print(f"Range: {g_gap_values[0]:.4f} to {g_gap_values[-1]:.4f} nS")
        print()

        results = []
        for g_gap in tqdm(g_gap_values, desc="g_gap sweep"):
            result = self.test_single_configuration(
                g_gap=g_gap,
                R_mem=100.0,  # Default
                tau_relax=60.0  # Default
            )
            results.append(result)

        return pd.DataFrame(results)

    def sweep_membrane_resistance(self, R_mem_values=None):
        """
        Sweep membrane resistance.
        """
        if R_mem_values is None:
            R_mem_values = np.logspace(1, 3, 10)  # 10 to 1000 MΩ

        print("\n" + "="*70)
        print("MEMBRANE RESISTANCE SWEEP")
        print("="*70 + "\n")

        print(f"Testing {len(R_mem_values)} values...")
        print(f"Range: {R_mem_values[0]:.1f} to {R_mem_values[-1]:.1f} MΩ")
        print()

        results = []
        for R_mem in tqdm(R_mem_values, desc="R_mem sweep"):
            result = self.test_single_configuration(
                g_gap=0.02,  # Default
                R_mem=R_mem,
                tau_relax=60.0  # Default
            )
            results.append(result)

        return pd.DataFrame(results)

    def sweep_relaxation_time(self, tau_values=None):
        """
        Sweep relaxation time constant.
        """
        if tau_values is None:
            tau_values = np.logspace(0, 3, 10)  # 1 to 1000 minutes

        print("\n" + "="*70)
        print("RELAXATION TIME CONSTANT SWEEP")
        print("="*70 + "\n")

        print(f"Testing {len(tau_values)} values...")
        print(f"Range: {tau_values[0]:.1f} to {tau_values[-1]:.1f} minutes")
        print()

        results = []
        for tau in tqdm(tau_values, desc="tau_relax sweep"):
            result = self.test_single_configuration(
                g_gap=0.02,  # Default
                R_mem=100.0,  # Default
                tau_relax=tau
            )
            results.append(result)

        return pd.DataFrame(results)

    def full_parameter_sweep(self, coarse=True):
        """
        Full combinatorial sweep of all parameters.

        Args:
            coarse: If True, use coarse grid (faster). If False, fine grid (slower).
        """
        print("\n" + "="*70)
        print("FULL PARAMETER SPACE SWEEP")
        print("="*70 + "\n")

        if coarse:
            g_gap_values = np.logspace(-2.5, -1.5, 5)  # 0.003 to 0.03 nS
            R_mem_values = np.logspace(1.5, 2.5, 5)    # 30 to 300 MΩ
            tau_values = np.logspace(1, 2.5, 5)        # 10 to 300 minutes
        else:
            g_gap_values = np.logspace(-3, -1, 10)
            R_mem_values = np.logspace(1, 3, 10)
            tau_values = np.logspace(0, 3, 10)

        total_tests = len(g_gap_values) * len(R_mem_values) * len(tau_values)

        print(f"Parameter combinations: {total_tests}")
        print(f"Estimated time: {total_tests * 0.5:.1f} seconds (~{total_tests * 0.5 / 60:.1f} minutes)")
        print()

        confirm = input("Continue with full sweep? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Sweep cancelled.")
            return None

        results = []
        combinations = list(product(g_gap_values, R_mem_values, tau_values))

        for g_gap, R_mem, tau in tqdm(combinations, desc="Full sweep"):
            result = self.test_single_configuration(g_gap, R_mem, tau)
            results.append(result)

        return pd.DataFrame(results)

    def plot_single_sweep(self, df, param_name, save_path=None):
        """
        Plot results from single parameter sweep.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Persistence ratio
        ax1.plot(df[param_name], df['persistence_ratio'], 'o-', linewidth=2, markersize=8)
        ax1.axhline(y=0.7, color='r', linestyle='--', label='Target threshold')
        ax1.set_xlabel(param_name, fontsize=12, fontweight='bold')
        ax1.set_ylabel('Persistence Ratio', fontsize=12, fontweight='bold')
        ax1.set_title(f'Pattern Persistence vs {param_name}', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        if 'g_gap' in param_name or 'tau' in param_name:
            ax1.set_xscale('log')

        # Voltage separation
        ax2.plot(df[param_name], df['voltage_separation'], 's-',
                linewidth=2, markersize=8, color='green')
        ax2.set_xlabel(param_name, fontsize=12, fontweight='bold')
        ax2.set_ylabel('Voltage Separation (mV)', fontsize=12, fontweight='bold')
        ax2.set_title(f'Bit Separation vs {param_name}', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        if 'g_gap' in param_name or 'tau' in param_name:
            ax2.set_xscale('log')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved plot: {save_path}")

        return fig

    def plot_heatmap(self, df, param1, param2, metric='persistence_ratio', save_path=None):
        """
        Plot 2D heatmap of parameter sweep.
        """
        # Pivot data
        pivot = df.pivot_table(values=metric, index=param2, columns=param1, aggfunc='mean')

        fig, ax = plt.subplots(figsize=(10, 8))

        sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn',
                   vmin=0, vmax=1, ax=ax, cbar_kws={'label': metric})

        ax.set_title(f'{metric} vs {param1} and {param2}',
                    fontsize=14, fontweight='bold')
        ax.set_xlabel(param1, fontsize=12, fontweight='bold')
        ax.set_ylabel(param2, fontsize=12, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved heatmap: {save_path}")

        return fig

    def find_optimal_parameters(self, df):
        """
        Find optimal parameter set from sweep results.
        """
        print("\n" + "="*70)
        print("OPTIMAL PARAMETER ANALYSIS")
        print("="*70 + "\n")

        # Best persistence ratio
        best_persistence = df.loc[df['persistence_ratio'].idxmax()]

        # Best voltage separation
        best_separation = df.loc[df['voltage_separation'].idxmax()]

        # Best combined score (weighted)
        df['combined_score'] = (0.7 * df['persistence_ratio'] +
                               0.3 * df['voltage_separation'] / df['voltage_separation'].max())
        best_combined = df.loc[df['combined_score'].idxmax()]

        print("Best Persistence Ratio:")
        print(f"  g_gap: {best_persistence['g_gap']:.4f} nS")
        print(f"  R_mem: {best_persistence['R_mem']:.1f} MΩ")
        print(f"  tau_relax: {best_persistence['tau_relax']:.1f} min")
        print(f"  Persistence: {best_persistence['persistence_ratio']:.3f}")
        print()

        print("Best Voltage Separation:")
        print(f"  g_gap: {best_separation['g_gap']:.4f} nS")
        print(f"  R_mem: {best_separation['R_mem']:.1f} MΩ")
        print(f"  tau_relax: {best_separation['tau_relax']:.1f} min")
        print(f"  Separation: {best_separation['voltage_separation']:.1f} mV")
        print()

        print("Best Combined Score:")
        print(f"  g_gap: {best_combined['g_gap']:.4f} nS")
        print(f"  R_mem: {best_combined['R_mem']:.1f} MΩ")
        print(f"  tau_relax: {best_combined['tau_relax']:.1f} min")
        print(f"  Persistence: {best_combined['persistence_ratio']:.3f}")
        print(f"  Separation: {best_combined['voltage_separation']:.1f} mV")
        print(f"  Combined score: {best_combined['combined_score']:.3f}")
        print()

        return {
            'best_persistence': best_persistence.to_dict(),
            'best_separation': best_separation.to_dict(),
            'best_combined': best_combined.to_dict()
        }


def run_quick_sweep():
    """
    Quick parameter sweep (for testing).
    """
    print("\n" + "="*70)
    print("QUICK PARAMETER SWEEP")
    print("="*70)

    sweeper = ParameterSweep()

    # Sweep gap junction (fastest)
    df_gap = sweeper.sweep_gap_junction(g_gap_values=np.logspace(-2.5, -1.5, 8))
    sweeper.plot_single_sweep(df_gap, 'g_gap', save_path='analysis/sweep_gap_junction.png')

    # Find optimal
    optimal = sweeper.find_optimal_parameters(df_gap)

    plt.show()


def run_comprehensive_sweep():
    """
    Comprehensive parameter sweep (takes longer).
    """
    print("\n" + "="*70)
    print("COMPREHENSIVE PARAMETER SWEEP")
    print("="*70)

    sweeper = ParameterSweep()

    # Individual sweeps
    print("\n1. Gap junction sweep...")
    df_gap = sweeper.sweep_gap_junction()
    sweeper.plot_single_sweep(df_gap, 'g_gap', save_path='analysis/sweep_gap_junction.png')

    print("\n2. Membrane resistance sweep...")
    df_Rmem = sweeper.sweep_membrane_resistance()
    sweeper.plot_single_sweep(df_Rmem, 'R_mem', save_path='analysis/sweep_membrane_resistance.png')

    print("\n3. Relaxation time sweep...")
    df_tau = sweeper.sweep_relaxation_time()
    sweeper.plot_single_sweep(df_tau, 'tau_relax', save_path='analysis/sweep_relaxation_time.png')

    # Full combinatorial (optional)
    print("\n4. Full parameter space sweep...")
    df_full = sweeper.full_parameter_sweep(coarse=True)

    if df_full is not None:
        # Save results
        df_full.to_csv('analysis/parameter_sweep_results.csv', index=False)
        print("\n✓ Results saved to analysis/parameter_sweep_results.csv")

        # Heatmaps
        sweeper.plot_heatmap(df_full, 'g_gap', 'R_mem',
                           save_path='analysis/heatmap_gap_Rmem.png')
        sweeper.plot_heatmap(df_full, 'g_gap', 'tau_relax',
                           save_path='analysis/heatmap_gap_tau.png')

        # Find optimal
        optimal = sweeper.find_optimal_parameters(df_full)

    plt.show()


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        run_quick_sweep()
    else:
        run_comprehensive_sweep()
