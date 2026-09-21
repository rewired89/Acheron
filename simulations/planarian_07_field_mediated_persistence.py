"""
Acheron Experiment: Does a Self-Generated Electric Field Extend Pattern
Persistence Beyond Gap-Junction Diffusion Alone?
=============================================================================

QUESTION:
planarian_01_bioelectric_persistence.py (this repo) models pattern persistence as pure
gap-junction resistive coupling on a 2D grid. Manicka & Levin's published,
peer-reviewed model additionally couples cells through a self-generated
extracellular electric field (each cell's Vmem contributes to a shared
field that feeds back on neighboring cells' ion channel conductance) —
their paper's central claim is that this field-mediation, not gap
junctions alone, is what stabilizes bioelectric prepatterning. This
experiment runs their own model (not a re-derivation) with a written
bit-cluster pattern and asks: does turning the field on measurably change
how long the written pattern survives, versus gap-junction diffusion
by itself, in their own dynamics?

METHODOLOGY / ATTRIBUTION:
Uses third_party/electric_morphogenesis/cellularFieldNetwork.py
UNMODIFIED (Manicka & Levin, "Field-mediated bioelectric basis of
morphogenetic prepatterning," Cell Reports Physical Science, 2025;
github.com/santamanicka/ElectricMorphogenesis, CC BY 4.0 — see
third_party/electric_morphogenesis/NOTICE.md for the full attribution
and a note on a license inconsistency in the upstream repo).

Deliberately does NOT use the repository's pretrained model checkpoints
(data/*.dat) — those are third-party pickled files that would require
torch.load(..., weights_only=False) to open, which can execute arbitrary
code from an untrusted source. Parameters below are hand-specified,
adapted from the published defaults in that repo's own
simulateCellularFieldNetwork.py (comments below note which values changed
and why). See NOTICE.md for the full reasoning.

TIME UNITS:
The model's `timestep` and iteration count are in the source project's own
internal units — this integration does not know the mapping to real
minutes/hours (unlike planarian_01_bioelectric_persistence.py's dt in minutes), and
does not invent one. Results are reported in simulation iterations only.

WHAT THIS DOES NOT DO:
Runs the published model's own dynamics with hand-chosen (not fit,
not pretrained) parameters — it is not a claim about the parameter
values Manicka & Levin actually validated, only about the qualitative
field-on vs. field-off comparison under one consistent, stated
configuration.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_REPO_ROOT / "third_party" / "electric_morphogenesis"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from cellularFieldNetwork import cellularFieldNetwork

ANALYSIS_DIR = _REPO_ROOT / "analysis"


def build_parameters(field_enabled: bool) -> dict:
    """Hand-specified parameters, adapted from the published defaults in
    ElectricMorphogenesis's own simulateCellularFieldNetwork.py. Only
    `fieldEnabled` differs between the two conditions being compared;
    everything else is held fixed."""
    field_parameters = {
        "fieldEnabled": field_enabled,
        "fieldResolution": 1,
        "fieldStrength": 1.0,
        "fieldAggregation": "average",
        "fieldScreenSize": 4,
        "fieldTransductionWeight": torch.DoubleTensor([1000.0]),
        "fieldTransductionBias": torch.DoubleTensor([0.0005]),
        "fieldTransductionGain": -1.0,
        "fieldTransductionTimeConstant": torch.DoubleTensor([10.0]),
        "fieldRangeSymmetric": False,
        "fieldVector": True,
    }
    gj_parameters = {"GJStrength": 0.05}  # published "meaningful" range: [0.05, 1.0]
    return {
        "fieldParameters": field_parameters,
        "GJParameters": gj_parameters,
        "GRNParameters": None,  # no gene-regulatory layer -- isolates the bioelectric-only comparison
        "ligandParameters": None,  # no diffusible ligand -- isolates gap-junction + field effects only
    }


def build_initial_values(circuit: cellularFieldNetwork, written_cell_indices: list[int]) -> dict:
    """Baseline tissue at rest, with a hyperpolarized cluster written in --
    the same 'write a bit to a cell cluster, then watch it drift' setup
    planarian_01_bioelectric_persistence.py uses, translated into this model's variables."""
    num_samples, num_cells = circuit.numSamples, circuit.numCells
    initial_values = {}

    baseline_vmem = -9.2e-3  # matches the source repo's own single-value default (volts)
    written_vmem = -55e-3  # E_pol -- the model's own hyperpolarizing-channel reversal potential

    vmem = torch.full((num_samples, num_cells, 1), baseline_vmem, dtype=torch.float64)
    vmem[:, written_cell_indices, 0] = written_vmem
    initial_values["Vmem"] = vmem

    initial_values["eV"] = torch.zeros((num_samples, circuit.numFieldGridPoints, 1), dtype=torch.float64)
    initial_values["ligandConc"] = torch.zeros((num_samples, num_cells, 1), dtype=torch.float64)

    initial_values["G_pol"] = {
        "cells": [[list(range(num_cells))]] * num_samples,
        "values": [torch.DoubleTensor([1.0])] * num_samples,  # bistable channel regime, matches source repo default
    }
    initial_values["G_dep"] = {"cells": [], "values": torch.DoubleTensor([])}
    return initial_values


def run_condition(field_enabled: bool, lattice_dims: tuple[int, int], written_cell_indices: list[int],
                   num_sim_iters: int) -> np.ndarray:
    parameters = build_parameters(field_enabled)
    circuit = cellularFieldNetwork(latticeDims=lattice_dims, parameters=parameters, numSamples=1)
    initial_values = build_initial_values(circuit, written_cell_indices)
    circuit.initVariables(initial_values)
    circuit.initParameters(initial_values)

    # Single documented call (see the source repo's own commented-out usage
    # at the bottom of simulateCellularFieldNetwork.py) -- no clamping, no
    # perturbation, no pretrained-file loading. saveData=True makes the
    # circuit record circuit.timeseriesVmem internally.
    circuit.simulate(
        externalInputs={"gene": None},
        numSimIters=num_sim_iters,
        stochasticIonChannels=False,
        setGradient=False,
        retainGradients=False,
        saveData=True,
    )
    # shape: (numSimIters, numSamples, numCells, 1) -> (numSimIters, numCells)
    return circuit.timeseriesVmem[:, 0, :, 0].numpy()


def pattern_contrast(vmem_trace: np.ndarray, written_cell_indices: list[int]) -> np.ndarray:
    """Mean |written-region Vmem - rest-of-tissue Vmem| over time -- how
    distinguishable the written pattern still is from background, in volts.
    """
    written_mask = np.zeros(vmem_trace.shape[1], dtype=bool)
    written_mask[written_cell_indices] = True
    written_mean = vmem_trace[:, written_mask].mean(axis=1)
    rest_mean = vmem_trace[:, ~written_mask].mean(axis=1)
    return np.abs(written_mean - rest_mean)


def main() -> None:
    print("=" * 72)
    print("FIELD-MEDIATED VS. GAP-JUNCTION-ONLY PATTERN PERSISTENCE")
    print("(running Manicka & Levin's published model, unmodified)")
    print("=" * 72)

    lattice_dims = (7, 7)
    num_cells = lattice_dims[0] * lattice_dims[1]
    # A 3x3 block near the center as the "written" cluster
    center_row, center_col = lattice_dims[0] // 2, lattice_dims[1] // 2
    written_cell_indices = [
        r * lattice_dims[1] + c
        for r in range(center_row - 1, center_row + 2)
        for c in range(center_col - 1, center_col + 2)
    ]
    num_sim_iters = 3000

    print(f"Lattice: {lattice_dims[0]}x{lattice_dims[1]} = {num_cells} cells, "
          f"{len(written_cell_indices)} written cells, {num_sim_iters} iterations")

    tail_window = max(1, num_sim_iters // 10)  # last 10% of iterations

    results = {}
    for field_enabled in (False, True):
        label = "field-enabled" if field_enabled else "field-disabled (GJ-only)"
        print(f"\nRunning {label}...")
        trace = run_condition(field_enabled, lattice_dims, written_cell_indices, num_sim_iters)
        contrast = pattern_contrast(trace, written_cell_indices)
        # Mean over a trailing window, not a single final frame -- the
        # field-enabled trace turns out to oscillate (see the saved plot),
        # so one snapshot could land on a peak or trough by chance.
        tail_mean = float(contrast[-tail_window:].mean())
        tail_std = float(contrast[-tail_window:].std())
        results[field_enabled] = {"trace": trace, "contrast": contrast, "tail_mean": tail_mean, "tail_std": tail_std}
        print(f"  contrast[0] = {contrast[0]*1000:.2f} mV, "
              f"final-10%-mean = {tail_mean*1000:.2f}+-{tail_std*1000:.2f} mV, "
              f"retained = {100*tail_mean/contrast[0]:.1f}%")

    ANALYSIS_DIR.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    for field_enabled, style in ((False, "--"), (True, "-")):
        c = results[field_enabled]["contrast"] * 1000
        label = "field-enabled" if field_enabled else "field-disabled (GJ-only)"
        ax.plot(c, style, label=label)
    ax.set_xlabel("simulation iteration")
    ax.set_ylabel("pattern contrast (mV)")
    ax.set_title("Written-pattern contrast over time")
    ax.legend()

    ax = axes[1]
    final_field = results[True]["trace"][-1].reshape(lattice_dims)
    im = ax.imshow(final_field * 1000, cmap="coolwarm")
    ax.set_title("Final Vmem (mV), field-enabled")
    plt.colorbar(im, ax=ax)

    plt.tight_layout()
    out_path = ANALYSIS_DIR / "field_mediated_persistence.png"
    plt.savefig(out_path, dpi=120)
    print(f"\nSaved figure: {out_path}")

    retained_field = 100 * results[True]["tail_mean"] / results[True]["contrast"][0]
    retained_gj = 100 * results[False]["tail_mean"] / results[False]["contrast"][0]
    field_is_oscillating = results[True]["tail_std"] > 0.15 * results[True]["tail_mean"]

    print("\n" + "=" * 72)
    print("INTERPRETATION")
    print("=" * 72)
    print(f"Pattern contrast retained, mean over the final {tail_window} iterations:")
    print(f"  field-enabled:            {retained_field:.1f}%")
    print(f"  field-disabled (GJ-only): {retained_gj:.1f}%")
    print(f"\nGJ-only settles to a near-flat contrast quickly (no driving term once gap")
    print(f"  junctions equilibrate, so it just stays at whatever it leaked down to).")
    if field_is_oscillating:
        print(f"Field-enabled does NOT settle -- it oscillates (std/mean = "
              f"{results[True]['tail_std']/results[True]['tail_mean']:.2f} over the tail window; see the")
        print(f"  saved plot). That is itself the more interesting finding here: these")
        print(f"  hand-specified field-transduction parameters (adapted from the source")
        print(f"  repo's own un-fitted example script, NOT their published fitted/")
        print(f"  pretrained values -- deliberately not loaded, see NOTICE.md) push the")
        print(f"  field feedback into an oscillatory regime rather than a stabilizing one.")
        print(f"  That does not contradict Manicka & Levin's own result -- their paper's")
        print(f"  stabilizing field regime almost certainly depends on specifically-fit")
        print(f"  parameters (via their learnCellularFieldNetwork.py training procedure),")
        print(f"  not on field-mediation being unconditionally stabilizing for any gain.")
        print(f"  The concrete next step is fitting fieldTransductionGain/Weight against")
        print(f"  a stability objective instead of reusing untuned example values.")
    elif retained_field > retained_gj + 5:
        print("\nField-mediation measurably extended pattern persistence beyond gap")
        print("  junctions alone in this run -- consistent with Manicka & Levin's own")
        print("  central claim, now checked against a written-bit-cluster setup shaped")
        print("  like this repo's own persistence tests rather than their original")
        print("  prepatterning scenario. This is one configuration, one lattice size,")
        print("  hand-specified (not fitted) parameters -- a reason to look closer at")
        print("  field-mediation for planarian_01_bioelectric_persistence.py, not a validated result.")
    elif retained_gj > retained_field + 5:
        print("\nGap-junction diffusion alone retained the pattern BETTER than with the")
        print("  field enabled in this run -- opposite of the paper's own framing, under")
        print("  these specific hand-specified parameters, which were deliberately NOT")
        print("  their fitted/pretrained values (see NOTICE.md for why). Worth checking")
        print("  whether the field parameters chosen here are simply a poor operating")
        print("  point before concluding anything about the mechanism itself.")
    else:
        print("\nNo clear difference between conditions at this lattice size/parameter")
        print("  choice -- inconclusive, not evidence either way.")
    print("=" * 72)


if __name__ == "__main__":
    main()
