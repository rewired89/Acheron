"""
Acheron Simulation 3: Tile Cross-Talk Map
==========================================

PURPOSE:
The existing simulator tuned g_gap = 0.005 nS to minimize cross-talk but
never formally validated what tile SPACING is actually required.

If two tiles are too close, gap junction coupling bleeds voltage from one
tile into its neighbor, corrupting the stored bit.

This simulation places two encoded tiles at varying separations and measures
the cross-talk percentage as a function of distance.

KEY QUESTION:
What is the minimum safe spacing between tiles such that cross-talk remains
below 5% after 24 hours?

This directly determines the maximum storage density of the Bio-Hard Drive.

OUTPUT:
- Cross-talk % vs tile separation (in cells and in micrometers)
- Voltage bleed-through map as a 2D heatmap at each separation
- Maximum storage density estimate (bits/mm²)
- Recommended tile spacing for hardware design
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Dict, Tuple
import os


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

# Physical cell dimensions (planarian somatic cell ~ 10–20 μm diameter)
# Using 15 μm as representative value
CELL_DIAMETER_UM = 15.0  # micrometers per cell

# Voltage parameters (from base simulator)
V_REST  = -50.0   # mV
V_HIGH  = -10.0   # mV  (bit 1)
V_LOW   = -80.0   # mV  (bit 0)
V_MID   = (V_HIGH + V_LOW) / 2.0  # decision boundary = -45 mV

# Base biophysical parameters
G_GAP_BASE  = 0.005   # nS
R_MEM_BASE  = 200.0   # MΩ
TAU_BASE    = 240.0   # min
C_MEM       = 5.0     # μF/cm²

# Simulation parameters
DT          = 0.5     # min
GRID_ROWS   = 30
CLUSTER_SZ  = 3       # 3×3 cells per tile


# ─────────────────────────────────────────────
# Cross-talk simulator
# ─────────────────────────────────────────────

class CrossTalkSimulator:
    """
    Measures voltage bleed between two adjacent encoded tiles.

    Tile A is encoded with bit=1 (V_HIGH).
    Tile B is encoded with bit=0 (V_LOW).
    The worst-case cross-talk is A→B and B→A simultaneously.
    """

    def __init__(self,
                 grid_cols: int,
                 tile_a_col_center: int,
                 tile_b_col_center: int,
                 g_gap: float = G_GAP_BASE,
                 dt: float = DT):
        self.rows = GRID_ROWS
        self.cols = grid_cols
        self.dt   = g_gap and dt
        self.g_gap = g_gap
        self.dt    = dt

        # Voltage grid at rest
        self.V = np.full((self.rows, self.cols), V_REST)

        # Write tile A (center row, column A) — bit 1
        half = CLUSTER_SZ // 2
        row_c = self.rows // 2
        self._tile_a_coords = []
        self._tile_b_coords = []

        for dr in range(-half, half + 1):
            for dc in range(-half, half + 1):
                ra, ca = row_c + dr, tile_a_col_center + dc
                rb, cb = row_c + dr, tile_b_col_center + dc
                if 0 <= ra < self.rows and 0 <= ca < self.cols:
                    self.V[ra, ca] = V_HIGH
                    self._tile_a_coords.append((ra, ca))
                if 0 <= rb < self.rows and 0 <= cb < self.cols:
                    self.V[rb, cb] = V_LOW
                    self._tile_b_coords.append((rb, cb))

        self.time = 0.0

    def step(self):
        """Single timestep of gap junction + membrane dynamics."""
        g = self.g_gap
        I_gap = np.zeros_like(self.V)
        I_gap[1:,  :] += g * (self.V[:-1, :] - self.V[1:,  :])
        I_gap[:-1, :] += g * (self.V[1:,  :] - self.V[:-1, :])
        I_gap[:,  1:] += g * (self.V[:, :-1] - self.V[:,  1:])
        I_gap[:, :-1] += g * (self.V[:,  1:] - self.V[:, :-1])

        I_mem = (V_REST - self.V) / (R_MEM_BASE * TAU_BASE)
        dV    = (I_gap + I_mem) / C_MEM * self.dt
        self.V += dV
        self.time += self.dt

    def run(self, duration_hours: float = 24.0) -> Dict:
        """Run simulation and measure cross-talk at the end."""
        n_steps = int(duration_hours * 60 / self.dt)
        for _ in range(n_steps):
            self.step()
        return self._measure_crosstalk()

    def _measure_crosstalk(self) -> Dict:
        """
        Quantify how much each tile's voltage has drifted toward the other.

        Cross-talk from B→A: how much has tile A (bit1) shifted toward V_LOW?
        Cross-talk from A→B: how much has tile B (bit0) shifted toward V_HIGH?
        """
        # Tile A: started at V_HIGH, any shift toward V_LOW is cross-talk
        va_mean = np.mean([self.V[r, c] for r, c in self._tile_a_coords])
        vb_mean = np.mean([self.V[r, c] for r, c in self._tile_b_coords])

        signal_range  = abs(V_HIGH - V_LOW)  # 70 mV
        xt_a = abs(va_mean - V_HIGH) / signal_range  # A drifted toward LOW
        xt_b = abs(vb_mean - V_LOW)  / signal_range  # B drifted toward HIGH

        worst_case_xt = max(xt_a, xt_b)

        # Are tiles still correctly classified?
        a_correct = va_mean > V_MID
        b_correct = vb_mean < V_MID

        return {
            'tile_a_mean_V':   va_mean,
            'tile_b_mean_V':   vb_mean,
            'crosstalk_a':     xt_a,
            'crosstalk_b':     xt_b,
            'worst_xt':        worst_case_xt,
            'a_correct':       a_correct,
            'b_correct':       b_correct,
            'both_correct':    a_correct and b_correct,
            'V_grid':          self.V.copy(),
        }


# ─────────────────────────────────────────────
# Sweep over separations
# ─────────────────────────────────────────────

def run_separation_sweep(
        separations_cells: List[int],
        g_gap_values: List[float],
        duration_hours: float = 24.0,
        output_dir: str = 'analysis') -> Dict:
    """
    Sweep tile-to-tile separation and gap junction conductance.

    Args:
        separations_cells: Gap between tiles in number of cells
        g_gap_values:      Gap junction conductances to test
        duration_hours:    Simulation duration
        output_dir:        Where to save plots
    """
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 65)
    print("ACHERON TILE CROSS-TALK MAP")
    print("=" * 65)

    results_matrix = np.zeros((len(g_gap_values), len(separations_cells)))
    correctness_matrix = np.zeros_like(results_matrix)

    grid_width = max(separations_cells) + CLUSTER_SZ * 4 + 10

    for gi, g_gap in enumerate(g_gap_values):
        print(f"\ng_gap = {g_gap:.4f} nS:")
        for si, sep in enumerate(separations_cells):
            # Position tile A at 1/3 of grid, tile B at 1/3 + sep + cluster_sz
            tile_a_col = CLUSTER_SZ + 2
            tile_b_col = tile_a_col + CLUSTER_SZ + sep

            actual_grid_cols = tile_b_col + CLUSTER_SZ + 3

            sim = CrossTalkSimulator(
                grid_cols=actual_grid_cols,
                tile_a_col_center=tile_a_col,
                tile_b_col_center=tile_b_col,
                g_gap=g_gap,
            )
            result = sim.run(duration_hours)

            xt_pct = result['worst_xt'] * 100
            results_matrix[gi, si]    = xt_pct
            correctness_matrix[gi, si] = float(result['both_correct'])

            sep_um = sep * CELL_DIAMETER_UM
            status = "OK" if result['both_correct'] else "FAIL"
            print(f"  sep={sep:2d} cells ({sep_um:.0f}μm): "
                  f"XT={xt_pct:5.1f}%  [{status}]")

    _plot_crosstalk(results_matrix, correctness_matrix,
                    separations_cells, g_gap_values,
                    duration_hours, output_dir)
    _print_summary(results_matrix, correctness_matrix,
                   separations_cells, g_gap_values)

    return {
        'crosstalk_matrix':   results_matrix,
        'correctness_matrix': correctness_matrix,
        'separations_cells':  separations_cells,
        'separations_um':     [s * CELL_DIAMETER_UM for s in separations_cells],
        'g_gap_values':       g_gap_values,
    }


def run_detailed_voltage_maps(output_dir: str = 'analysis'):
    """
    Produce 2D voltage maps at 3 separation distances for visual inspection.
    """
    separations = [2, 6, 12]  # cells
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("Voltage Maps: Two Adjacent Tiles After 24 Hours\n"
                 "Left = dangerously close, Right = safely separated",
                 fontsize=12, fontweight='bold')

    for ax, sep in zip(axes, separations):
        tile_a_col = CLUSTER_SZ + 2
        tile_b_col = tile_a_col + CLUSTER_SZ + sep
        grid_cols  = tile_b_col + CLUSTER_SZ + 3

        sim = CrossTalkSimulator(grid_cols=grid_cols,
                                 tile_a_col_center=tile_a_col,
                                 tile_b_col_center=tile_b_col)
        result = sim.run(24.0)

        im = ax.imshow(result['V_grid'], cmap='RdBu_r',
                       vmin=V_LOW - 5, vmax=V_HIGH + 5,
                       aspect='auto', interpolation='nearest')
        sep_um = sep * CELL_DIAMETER_UM
        xt     = result['worst_xt'] * 100
        status = "PASS" if result['both_correct'] else "FAIL"
        ax.set_title(f'Separation: {sep} cells ({sep_um:.0f} μm)\n'
                     f'Max cross-talk: {xt:.1f}%  [{status}]',
                     fontsize=10)
        ax.set_xlabel('Cell Column')
        ax.set_ylabel('Cell Row')
        plt.colorbar(im, ax=ax, label='Vmem (mV)')

        # Mark tile centers
        row_c = GRID_ROWS // 2
        ax.plot(tile_a_col, row_c, 'w^', markersize=10, label='Tile A (bit=1)')
        ax.plot(tile_b_col, row_c, 'wv', markersize=10, label='Tile B (bit=0)')
        ax.legend(fontsize=8, loc='upper right')

    plt.tight_layout()
    path = os.path.join(output_dir, 'tile_voltage_maps.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"Voltage maps saved: {path}")
    plt.close(fig)


def _plot_crosstalk(results_matrix, correctness_matrix,
                    separations_cells, g_gap_values,
                    duration_hours, output_dir):
    sep_um = [s * CELL_DIAMETER_UM for s in separations_cells]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Acheron Tile Cross-Talk Analysis\n"
                 "Minimum safe tile spacing for independent bit storage",
                 fontsize=13, fontweight='bold')

    colors = ['green', 'blue', 'orange', 'red', 'purple']

    # Panel 1: Cross-talk % vs separation for each g_gap
    ax = axes[0]
    for gi, (g_gap, col) in enumerate(zip(g_gap_values, colors)):
        ax.plot(sep_um, results_matrix[gi], '-o', color=col, linewidth=2,
                markersize=6, label=f'g_gap={g_gap:.4f} nS')
    ax.axhline(5.0,  color='black', linestyle='--', linewidth=1.5,
               label='5% threshold (target)')
    ax.axhline(10.0, color='gray',  linestyle=':', linewidth=1,
               label='10% threshold (marginal)')
    ax.set_xlabel('Tile Separation (μm)')
    ax.set_ylabel('Max Cross-Talk (%)')
    ax.set_title(f'Cross-Talk vs Tile Spacing\nAfter {duration_hours}h')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, min(results_matrix.max() * 1.1, 100))

    # Panel 2: Correctness heatmap
    ax2 = axes[1]
    im  = ax2.imshow(correctness_matrix, aspect='auto',
                     cmap='RdYlGn', vmin=0, vmax=1, origin='lower')
    ax2.set_xticks(range(len(separations_cells)))
    ax2.set_xticklabels([f'{u:.0f}μm' for u in sep_um], rotation=45, fontsize=8)
    ax2.set_yticks(range(len(g_gap_values)))
    ax2.set_yticklabels([f'{g:.4f}nS' for g in g_gap_values], fontsize=8)
    ax2.set_xlabel('Tile Separation')
    ax2.set_ylabel('Gap Junction Conductance')
    ax2.set_title('Both Tiles Correctly Read\n(green = yes, red = no)')
    plt.colorbar(im, ax=ax2, label='P(correct)')
    for i in range(len(g_gap_values)):
        for j in range(len(separations_cells)):
            ax2.text(j, i, 'OK' if correctness_matrix[i,j] > 0.5 else 'FAIL',
                    ha='center', va='center', fontsize=8, fontweight='bold',
                    color='black')

    # Panel 3: Storage density vs minimum spacing
    ax3 = axes[2]
    # At each g_gap, find minimum spacing where XT < 5%
    min_spacings_um = []
    for gi in range(len(g_gap_values)):
        safe = [sep_um[si] for si, xt in enumerate(results_matrix[gi])
                if xt < 5.0]
        min_spacings_um.append(min(safe) if safe else float('inf'))

    # Storage density = 1 / (tile_footprint)²
    # tile_footprint = CLUSTER_SZ * cell_diameter + min_spacing
    densities = []
    for min_sp in min_spacings_um:
        if min_sp == float('inf'):
            densities.append(0)
        else:
            tile_pitch_um  = CLUSTER_SZ * CELL_DIAMETER_UM + min_sp  # μm
            tile_pitch_mm  = tile_pitch_um / 1000.0
            bits_per_mm2   = 1.0 / (tile_pitch_mm ** 2)
            densities.append(bits_per_mm2)

    bars = ax3.bar(range(len(g_gap_values)), densities,
                   color=colors[:len(g_gap_values)], alpha=0.8)
    ax3.set_xticks(range(len(g_gap_values)))
    ax3.set_xticklabels([f'{g:.4f}' for g in g_gap_values],
                        rotation=45, fontsize=9)
    ax3.set_xlabel('Gap Junction Conductance (nS)')
    ax3.set_ylabel('Max Storage Density (bits/mm²)')
    ax3.set_title('Achievable Storage Density\n(at <5% cross-talk threshold)')
    ax3.grid(True, alpha=0.3, axis='y')
    for bar, density, ms in zip(bars, densities, min_spacings_um):
        if density > 0:
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.02,
                    f'{density:.0f}\nbits/mm²',
                    ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    path = os.path.join(output_dir, 'tile_crosstalk_map.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    print(f"\nPlot saved: {path}")
    plt.close(fig)


def _print_summary(results_matrix, correctness_matrix,
                   separations_cells, g_gap_values):
    sep_um = [s * CELL_DIAMETER_UM for s in separations_cells]

    print()
    print("=" * 65)
    print("CROSS-TALK ANALYSIS — SUMMARY")
    print("=" * 65)

    for gi, g_gap in enumerate(g_gap_values):
        # Find minimum safe separation (<5% XT)
        safe_seps = [(separations_cells[si], sep_um[si])
                     for si, xt in enumerate(results_matrix[gi])
                     if xt < 5.0]
        if safe_seps:
            min_cells, min_um = safe_seps[0]
            tile_pitch = CLUSTER_SZ * CELL_DIAMETER_UM + min_um
            density    = 1.0 / (tile_pitch / 1000.0)**2
            print(f"g_gap={g_gap:.4f} nS: min spacing = {min_cells} cells "
                  f"({min_um:.0f} μm) → density = {density:.0f} bits/mm²")
        else:
            print(f"g_gap={g_gap:.4f} nS: NO safe spacing found "
                  f"(cross-talk always >5%)")

    print()
    print("DESIGN RECOMMENDATION:")
    print(f"  Current simulator uses g_gap = {G_GAP_BASE} nS")
    print(f"  Run this sweep to find minimum tile spacing for the Bio-RAID layout.")
    print()
    print("  Key constraint: density is expected ~4 bits/mm².")
    print("  This is NOT competitive with silicon — that is not the value prop.")
    print("  Frame as: N bits in indestructible self-healing substrate.")
    print("=" * 65)


if __name__ == '__main__':
    separations = list(range(1, 20, 2))          # 1, 3, 5, ... 19 cells
    g_gaps      = [0.001, 0.005, 0.01, 0.02]    # nS

    results = run_separation_sweep(
        separations_cells=separations,
        g_gap_values=g_gaps,
        duration_hours=24.0,
    )

    run_detailed_voltage_maps()

    print("\nDone. Check analysis/ directory for plots.")
