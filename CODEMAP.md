# CODEMAP.md

Structural map of the Acheron repository. Generated in a single pass
(44 source files: 43 `.py` + 1 `.js`, well under the 150-file incremental
mapping threshold; one codebase, no distinct services/apps to split by).

**Scoping decisions, stated up front so they're not mistaken for gaps:**
- Acheron has no web app, API/routes, database layer, auth, background
  jobs, or frontend/backend split. Those sections are omitted rather than
  filled with "N/A" per entry.
- Small private numerical helpers (e.g. a single-line clipping or gradient
  function prefixed `_`) are listed under one combined "internal helpers"
  entry per file instead of one full template block each, per the
  instruction to skip trivial symbols. Classes and any function imported by
  another module, or serving as a script's entry point, get a full entry.
- `docs/`, `patents/`, `partnerships/` are documentation, not source, and
  are out of scope for this map (see `CLAUDE.md` for what's in them).
- This map reflects the code as of September 2026. **The source is always
  authoritative over this file if they disagree.**

---

## analysis/ — reusable, tested analysis methods

### `analysis/hidden_state_model.py`
Purpose: latent-threshold probit model of planarian "hidden regenerative
memory," reimplemented from tasmorpho (Blattner 2026), validated to 6
decimal places against a real run of the original (see `docs/
THIRD_PARTY_METHODS.md`). Only module in `analysis/` with no repo-internal
dependencies.

- name: `CountDatum`
  type: class (frozen dataclass)
  file: analysis/hidden_state_model.py
  purpose: one reconstructed published phenotype-count observation (label, successes, trials, role, description)
  inputs: none (data holder)
  outputs: none
  dependencies: none
  used_by: `COUNTS` module-level tuple, `negative_log_likelihood`, `closed_form_estimate`
  side_effects: none

- name: `phi_cdf`, `phi_inv`
  type: function
  file: analysis/hidden_state_model.py
  purpose: standard normal CDF / inverse CDF wrappers around `statistics.NormalDist`
  inputs: `x: float` / `p: float`
  outputs: `float`
  dependencies: `statistics.NormalDist`
  used_by: `p_immediate`, `p_challenge_given_sh`, `closed_form_estimate`, tests
  side_effects: none

- name: `p_immediate`, `p_challenge_given_sh`
  type: function
  file: analysis/hidden_state_model.py
  purpose: model probabilities (immediate double-headed outcome; challenge-reveal outcome given single-headed)
  inputs: `mu: float` (and `theta_ch: float` for the second)
  outputs: `float` probability
  dependencies: `phi_cdf`
  used_by: `negative_log_likelihood`, `fit`, `delta_method_interval` (via closures), tests
  side_effects: none

- name: `negative_log_likelihood`
  type: function
  file: analysis/hidden_state_model.py
  purpose: NLL of the 4-parameter model against `COUNTS`, minimized by `fit`
  inputs: `params: np.ndarray` (mu_8OH, mu_nigericin, mu_monensin, theta_ch)
  outputs: `float`
  dependencies: `p_immediate`, `p_challenge_given_sh`, `COUNTS`
  used_by: `fit` (via scipy cross-check), `_finite_diff_hessian`
  side_effects: none

- name: `closed_form_estimate`
  type: function
  file: analysis/hidden_state_model.py
  purpose: closed-form MLE for the 4 parameters (the model is exactly identified)
  inputs: none (reads module-level `COUNTS`)
  outputs: `np.ndarray` of 4 params
  dependencies: `phi_inv`, `phi_cdf`, `COUNTS`
  used_by: `fit`, tests
  side_effects: none

- name: `fit`
  type: function
  file: analysis/hidden_state_model.py
  purpose: fits the model, cross-checks against scipy Nelder-Mead, computes held-out challenge-penetrance predictions for nigericin/monensin via the delta method
  inputs: `cross_check_with_scipy: bool = True`
  outputs: `FitResult` (params, cov, nelder_mead_agrees, held-out predictions)
  dependencies: `closed_form_estimate`, `negative_log_likelihood`, `_finite_diff_hessian`, `delta_method_interval`, `p_challenge_given_sh`, `scipy.optimize.minimize` (optional)
  used_by: `experiments/handoff_pool_imperfect_healing.py` (imports `fit as fit_hidden_state_model`), tests
  side_effects: none

- name: internal helpers (`_clip_prob`, `_finite_diff_gradient`, `_finite_diff_hessian`, `delta_method_interval`, `FitResult`)
  type: function/class (group)
  file: analysis/hidden_state_model.py
  purpose: numeric plumbing (probability clipping, finite-difference gradient/Hessian, delta-method CI, the fit-result container)
  dependencies: numpy
  used_by: `fit`
  side_effects: none

### `analysis/memory_geometry.py`
Purpose: Q/R/K_mem dominant write-axis method, generalized from tasmorpho's
BETSE-specific script to accept perturbation trials from any substrate.

- name: `PerturbationTrial`
  type: class (dataclass)
  file: analysis/memory_geometry.py
  purpose: one (delta, observable-outcome) perturbation sample
  dependencies: none
  used_by: `compute_write_axis`, `experiments/write_axis_gardner.py`, `tests/test_memory_geometry.py`
  side_effects: none

- name: `WriteAxisResult`
  type: class (dataclass)
  file: analysis/memory_geometry.py
  purpose: result container (dominant axis, R, K_mem, etc.) returned by `compute_write_axis`
  dependencies: none
  used_by: `compute_write_axis` callers
  side_effects: none

- name: `compute_write_axis`
  type: function
  file: analysis/memory_geometry.py
  purpose: finds the dominant linear write-axis and its efficiency/symmetry (K_mem) from a list of perturbation trials
  inputs: `trials: list[PerturbationTrial]`, `ridge: float = 1e-8`
  outputs: `WriteAxisResult`
  dependencies: numpy, `PerturbationTrial`
  used_by: `experiments/write_axis_gardner.py`, `tests/test_memory_geometry.py`
  side_effects: none

### `analysis/reservoir_benchmarks.py`
Purpose: NARMA-10 sequence generation, ridge-regression readout, and
memory-capacity benchmark, generalized from NeuromorphicMyceliumChip.

- name: `generate_narma10`
  type: function
  file: analysis/reservoir_benchmarks.py
  purpose: generates the standard NARMA-10 benchmark input/target sequence
  inputs: `n_steps: int`, `order: int = 10`, `seed: Optional[int]`
  outputs: `tuple[np.ndarray, np.ndarray]` (input, target)
  dependencies: numpy
  used_by: `run_narma10_benchmark`, `experiments/reservoir_benchmark_gardner.py`, tests
  side_effects: none

- name: `fit_ridge_readout`
  type: function
  file: analysis/reservoir_benchmarks.py
  purpose: fits a ridge-regression readout layer from reservoir states to a target signal
  inputs: reservoir states, target, ridge coefficient
  outputs: `ReadoutResult`
  dependencies: numpy, `_nrmse`
  used_by: `run_narma10_benchmark`, tests
  side_effects: none

- name: `tapped_delay_states`
  type: function
  file: analysis/reservoir_benchmarks.py
  purpose: builds a tapped-delay-line feature matrix from a 1D signal, used as a trivial/reference "reservoir"
  inputs: `x: np.ndarray`, `n_taps: int = 5`
  outputs: `np.ndarray`
  dependencies: numpy
  used_by: tests, `run_narma10_benchmark` callers
  side_effects: none

- name: `run_narma10_benchmark`
  type: function
  file: analysis/reservoir_benchmarks.py
  purpose: end-to-end NARMA-10 benchmark: generate sequence, drive a caller-supplied reservoir, fit readout, report NRMSE improvement over predicting the mean
  inputs: a reservoir-state function/substrate, benchmark length, seed
  outputs: `ReadoutResult` and related metrics
  dependencies: `generate_narma10`, `fit_ridge_readout`, `_nrmse`
  used_by: `experiments/reservoir_benchmark_gardner.py`, tests
  side_effects: none

- name: `memory_capacity`
  type: function
  file: analysis/reservoir_benchmarks.py
  purpose: standard reservoir-computing memory-capacity metric (does the substrate's current state predict past inputs at various lags)
  outputs: `MemoryCapacityResult`
  dependencies: numpy
  used_by: `experiments/reservoir_benchmark_gardner.py`, tests
  side_effects: none

- name: `ReadoutResult`, `MemoryCapacityResult`, `_nrmse` (internal helper)
  type: class/function (group)
  file: analysis/reservoir_benchmarks.py
  purpose: result containers and the NRMSE metric used throughout the file
  dependencies: numpy
  used_by: functions above
  side_effects: none

### `analysis/visualize_competitive_landscape.py`
Purpose: generates comparison charts (lifespan, feature matrix, cost of
ownership, market positioning) of Acheron vs. named competitors, for use in
pitch materials. **Contains hardcoded competitor figures (e.g. lifespans in
months) that should be checked against `docs/SCIENTIFIC_AUDIT_2026.md` and
`docs/COMPETITIVE_ANALYSIS.md` before reuse, this script predates this
project's later competitor research (mycelium memristor, Biomemory, the
"adjacent research not competitors" reframing of Cortical Labs/Koniku/
FinalSpark) and has not been updated to match it.**

- name: `plot_lifespan_comparison`, `plot_feature_matrix`, `plot_cost_of_ownership`, `plot_market_positioning`
  type: function
  file: analysis/visualize_competitive_landscape.py
  purpose: each renders one matplotlib chart comparing Acheron to competitors on a specific axis
  inputs: none (hardcoded data)
  outputs: none (side effect only)
  dependencies: matplotlib, numpy, seaborn
  used_by: `generate_all_visualizations`
  side_effects: writes/shows matplotlib figures

- name: `generate_all_visualizations`
  type: function
  file: analysis/visualize_competitive_landscape.py
  purpose: entry point, calls all four plot functions
  dependencies: the four plot functions above
  used_by: `if __name__ == '__main__'` block
  side_effects: writes/shows matplotlib figures

---

## encoder/ — binary <-> bioelectric pattern translation software layer

### `encoder/bioelectric_encoder.py`
Purpose: the original planarian/optogenetic-DMD encoder. Translates a
binary string into a spatial voltage pattern (grid coordinates + target
voltage per bit-cluster) for optogenetic writing. Positioned in project
docs as the licensable "software layer" differentiator.

- name: `BioelectricEncoder`
  type: class
  file: encoder/bioelectric_encoder.py
  purpose: encodes/decodes binary strings to/from spatial voltage-pattern grids with redundancy (multiple cells/bit) and spatial isolation
  inputs: grid size, cells-per-bit, and (per call) a binary string or voltage grid
  outputs: voltage-pattern grid (encode) or decoded binary string (decode)
  dependencies: numpy, matplotlib, json
  used_by: `experiments/interactive_demo.py`, `experiments/ml_pattern_optimizer.py`, `experiments/phase2_bio_raid_simulator.py`
  side_effects: none (pure data transform; plotting methods, if any, write figures)

- name: `demo_encoder`
  type: function
  file: encoder/bioelectric_encoder.py
  purpose: standalone demonstration of encode/decode round-trip
  dependencies: `BioelectricEncoder`
  used_by: `if __name__ == '__main__'` block
  side_effects: prints to stdout, may show a plot

### `encoder/bacterial_toggle_encoder.py`
Purpose: sibling encoder for the *B. subtilis* pathway, explicitly NOT a
replacement for `bioelectric_encoder.py` (see its own docstring's
planarian-vs-bacterial comparison table). Encodes binary data as a
per-colony induction protocol (JSON, usable as a bench instruction sheet)
targeting the same Gardner-topology circuit modeled in `simulations/
gardner_toggle_circuit.py`.

- name: `BacterialToggleEncoder`
  type: class
  file: encoder/bacterial_toggle_encoder.py
  purpose: encodes a binary string into per-colony target states and a chemical/thermal induction protocol; decodes reporter-assay readouts back to binary
  inputs: binary string, or per-colony reporter readings
  outputs: induction protocol (JSON-serializable) or decoded binary string
  dependencies: none beyond stdlib/json
  used_by: `if __name__ == '__main__'` demo only (`demo_encoder`); not yet imported by any simulation or experiment script
  side_effects: none

- name: `demo_encoder`
  type: function
  file: encoder/bacterial_toggle_encoder.py
  purpose: standalone demonstration of `BacterialToggleEncoder`
  dependencies: `BacterialToggleEncoder`
  used_by: `if __name__ == '__main__'` block
  side_effects: prints to stdout

---

## simulations/ — the actual scientific models

This directory is the project's core. Files are grouped below by which
generation/organism they belong to, not alphabetically, since that's how
they depend on each other.

### Planarian / passive-persistence generation (Phase 1, now known incomplete)

- name: `PlanarianTissueModel`
  type: class
  file: simulations/bioelectric_persistence.py
  purpose: original 2D gap-junction-coupled planarian tissue model; the "24h persistence" claim later found to be a zero-noise artifact (`docs/SCIENTIFIC_AUDIT_2026.md` Part 8)
  inputs: grid size, dt, and (per call) a bit pattern to write
  outputs: voltage-grid state over time; integrity metrics
  dependencies: numpy, scipy.sparse
  used_by: `experiments/interactive_demo.py`, `experiments/ml_pattern_optimizer.py`, `experiments/parameter_sweep.py`, `experiments/phase2_bio_raid_simulator.py`
  side_effects: none (state lives on the instance)

- name: `demo_single_bit_storage`, `demo_multi_bit_storage`
  type: function
  file: simulations/bioelectric_persistence.py
  purpose: standalone demonstrations of the model
  dependencies: `PlanarianTissueModel`
  used_by: `if __name__ == '__main__'` block
  side_effects: prints/plots

- name: `NoiseProfile`, `NoisyPlanarianTissue`
  type: class (dataclass, class)
  file: simulations/noise_floor_characterizer.py
  purpose: adds four realistic biological noise sources (channel shot noise, cell-to-cell variability, metabolic noise, thermal noise) on top of the base persistence model; this is the file that found the 24h claim doesn't survive realistic noise
  inputs: noise parameters; a bit pattern to write
  outputs: integrity/SNR over time under each noise scenario
  dependencies: numpy
  used_by: `run_noise_sweep`, cited extensively in `docs/SCIENTIFIC_AUDIT_2026.md` Part 8
  side_effects: none

- name: `run_noise_sweep`, `setup_test_pattern`
  type: function
  file: simulations/noise_floor_characterizer.py
  purpose: runs the noise-floor sweep (ideal/mild/realistic/severe) and prints/plots the integrity-vs-noise result table
  dependencies: `NoisyPlanarianTissue`
  used_by: `if __name__ == '__main__'` block
  side_effects: prints, writes plots (`_plot_results`), stdout summary (`_print_summary`)

- name: `OptogeneticConfig`, `OptogeneticCellModel`, `WriteFidelityAnalyzer`
  type: class (dataclass, class, class)
  file: simulations/optogenetic_write_fidelity.py
  purpose: models write-side error (ChR2 expression variability, Beer-Lambert light attenuation with tissue depth, photocurrent kinetics) separate from the storage/noise question
  outputs: write-fidelity heatmap vs. expression variability x tissue depth
  dependencies: numpy
  used_by: `run_write_fidelity_analysis`; not imported elsewhere
  side_effects: none

- name: `run_write_fidelity_analysis`
  type: function
  file: simulations/optogenetic_write_fidelity.py
  purpose: entry point for the write-fidelity sweep
  dependencies: `WriteFidelityAnalyzer`
  used_by: `if __name__ == '__main__'` block
  side_effects: writes plots to `output_dir`

- name: `CrossTalkSimulator`
  type: class
  file: simulations/tile_crosstalk_map.py
  purpose: places two encoded tiles at varying separation and measures voltage bleed-through, to determine minimum safe tile spacing/storage density
  dependencies: numpy
  used_by: `run_separation_sweep`, `run_detailed_voltage_maps`; not imported elsewhere
  side_effects: none

- name: `run_separation_sweep`, `run_detailed_voltage_maps`
  type: function
  file: simulations/tile_crosstalk_map.py
  purpose: entry points running the cross-talk sweep and producing detailed voltage maps
  dependencies: `CrossTalkSimulator`
  used_by: `if __name__ == '__main__'` block
  side_effects: writes plots (`_plot_crosstalk`), prints summary (`_print_summary`)

- name: `PulseType`, `BioelectricPacket`, `BioCable`, `BioNetNode`, `BioNetSimulator`
  type: class (Enum, dataclass, class, class, class)
  file: simulations/bionet_propagation.py
  purpose: speculative "bioelectric internet" — voltage-wave propagation through gap-junction chains connecting multiple storage tiles, with self-healing mesh routing. Standalone from the rest of the simulation suite (see `used_by`: none confirmed)
  dependencies: numpy, scipy.sparse
  used_by: unknown (no other file in the repo imports this module)
  side_effects: none

- name: `demo_simple_transmission`, `demo_self_healing`, `demo_mesh_network`
  type: function
  file: simulations/bionet_propagation.py
  purpose: standalone demonstrations of `BioNetSimulator`
  dependencies: `BioNetSimulator` and related classes
  used_by: `if __name__ == '__main__'` block
  side_effects: prints/plots

### B. subtilis / engineered-circuit generation (current, better-grounded direction)

- name: `GardnerParams`, `GardnerToggleCell`
  type: class (dataclass, class)
  file: simulations/gardner_toggle_circuit.py
  purpose: the Gardner et al. (2000) two-repressor genetic toggle switch, built from real Bacillus BioBrick Box promoter parts; the engineered-circuit fix for passive persistence failing. Found the promoter-mismatch-collapses-bistability design constraint
  inputs: `GardnerParams` (promoter strengths, etc.); a bit to write
  outputs: genetic state (u/v repressor levels) and a derived voltage-output fidelity over time
  dependencies: numpy
  used_by: `run_persistence`, `experiments/reservoir_benchmark_gardner.py`, `experiments/write_axis_gardner.py`, `simulations/regrowth_state_inheritance.py`, `simulations/native_oscillation_interference.py`
  side_effects: none

- name: `run_persistence`
  type: function
  file: simulations/gardner_toggle_circuit.py
  purpose: runs a single write-and-hold trial for the toggle cell and reports genetic/voltage fidelity at a given time
  inputs: `bit: int`, `params: GardnerParams`, `hours: float = 24.0`
  outputs: fidelity metrics
  dependencies: `GardnerToggleCell`
  used_by: `main` (in the same file), other simulations that reuse this circuit
  side_effects: none

- name: `TileNoise`, `BacterialTile`
  type: class (dataclass, class)
  file: simulations/biofilm_tile_handoff.py
  purpose: single-colony bistable+noise tile model with `write`, `step`, `read`, and `reset_and_heal` (the write -> transfer -> self-heal-for-reuse cycle described in `docs/INVESTOR_PITCH.md`'s "Full Goal" section)
  inputs: noise config; bit to write; per-step external drive
  outputs: current voltage/read bit
  dependencies: numpy
  used_by: `propagate_handoff`, `run_handoff_chain`, `experiments/handoff_pool_imperfect_healing.py`
  side_effects: mutates instance voltage state via `step`/`write`/`reset_and_heal`

- name: `propagate_handoff`
  type: function
  file: simulations/biofilm_tile_handoff.py
  purpose: models the K+ wave handoff, drives a destination tile toward the source's current voltage for a duration, then decouples
  inputs: `source: BacterialTile`, `dest: BacterialTile`, duration, coupling strength
  outputs: none (mutates `dest` in place)
  dependencies: `BacterialTile.step`
  used_by: `run_handoff_chain`, `experiments/handoff_pool_imperfect_healing.py`
  side_effects: mutates `dest`'s voltage state

- name: `run_handoff_chain`
  type: function
  file: simulations/biofilm_tile_handoff.py
  purpose: simulates a full chain of write -> hold -> handoff -> heal -> repeat cycles, returns the bit read after each handoff
  dependencies: `BacterialTile`, `propagate_handoff`
  used_by: `main` (in the same file)
  side_effects: none (returns a list; internal tiles are ephemeral)

- name: `RegrowthConfig`
  type: class (dataclass)
  file: simulations/regrowth_state_inheritance.py
  purpose: config for the "does self-healing regrowth actually inherit the engineered state" experiment (as opposed to an externally-controlled handoff)
  dependencies: none
  used_by: `run_regrowth_trial`
  side_effects: none

- name: `run_regrowth_trial`, `sweep_surviving_fraction`
  type: function
  file: simulations/regrowth_state_inheritance.py
  purpose: models a fragment as surviving + naive (neoblast-derived) sub-populations under mean-field coupling from `gardner_toggle_circuit.py`/`biofilm_tile_handoff.py` physics, and sweeps the surviving fraction to see if the regenerated organism ends up holding the correct bit
  dependencies: `simulations.gardner_toggle_circuit`, `simulations.biofilm_tile_handoff` physics (reused, not reimported directly per current code, verify before assuming a direct import)
  used_by: `main` (in the same file); referenced in `simulations/organism_comparison_summary.py`'s cross-organism comparison
  side_effects: none

- name: `run_colony_trial`, `sweep_surviving_fraction`
  type: function
  file: simulations/bacterial_colony_regrowth.py
  purpose: *B. subtilis*-native sibling of `regrowth_state_inheritance.py`; colony damage-then-regrowth-by-division scenario for the engineered circuit
  dependencies: `simulations.gardner_toggle_circuit` physics
  used_by: `main` (in the same file); `simulations/organism_comparison_summary.py`
  side_effects: none

- name: `simulate_methylation_lineage`, `population_readout`, `sweep_fidelity`
  type: function
  file: simulations/methylation_bit_encoding.py
  purpose: models DNA-methylation-based bit storage (a candidate mechanism distinct from the Gardner circuit) across cell divisions, using two real, differently-sourced maintenance-fidelity anchors (99.9% and 96%, see `docs/SCIENTIFIC_AUDIT_2026.md` Part 11)
  dependencies: numpy
  used_by: `main` (in the same file); `simulations/methylation_regeneration_transfer.py`; `simulations/organism_comparison_summary.py`
  side_effects: none

- name: `run_regrowth_trial`, `sweep_surviving_fraction`
  type: function
  file: simulations/methylation_regeneration_transfer.py
  purpose: colony-damage-then-regrowth scenario for the methylation mechanism specifically (mirrors `bacterial_colony_regrowth.py`'s structure, swept across both real fidelity anchors)
  dependencies: `simulations.methylation_bit_encoding`
  used_by: `main` (in the same file); `simulations/organism_comparison_summary.py`
  side_effects: none

- name: `run_all`
  type: function
  file: simulations/organism_comparison_summary.py
  purpose: runs the three directly comparable regeneration/regrowth tests side by side (planarian circuit, *B. subtilis* circuit, *B. subtilis* methylation at both fidelity anchors) and ranks them by wet-lab risk still hidden, this is the source of "B. subtilis-first" in `CLAUDE.md`
  inputs: `fractions: List[float]`, `n_trials: int = 10`
  outputs: `Dict` of results per mechanism
  dependencies: `simulations.regrowth_state_inheritance`, `simulations.bacterial_colony_regrowth`, `simulations.methylation_regeneration_transfer`
  used_by: `main` (in the same file)
  side_effects: none

- name: `ambient_oscillation_offset`, `run_interference_trial`, `sweep_amplitude`
  type: function
  file: simulations/native_oscillation_interference.py
  purpose: adds *B. subtilis*'s real native potassium-wave signaling (Prindle et al. 2015 period range) as an external perturbation to a written `GardnerToggleCell`'s membrane voltage only, found it can corrupt a voltage read even when the genetic circuit's data is intact
  dependencies: `simulations.gardner_toggle_circuit.GardnerToggleCell`
  used_by: `main` (in the same file); the finding is reused/re-tested by `simulations/eis_readout_interference.py`
  side_effects: none

- name: `run_trial_trajectory`, `eis_style_read`, `sweep_windows`
  type: function
  file: simulations/eis_readout_interference.py
  purpose: tests whether reading via electrical impedance spectroscopy (integrating over a frequency sweep) is immune to the same native-oscillation interference found in `native_oscillation_interference.py`; found a single fast EIS sweep is NOT immune, only recovers accuracy once the integration window spans a full oscillation period (~3h)
  dependencies: same interference model as `native_oscillation_interference.py`
  used_by: `main` (in the same file)
  side_effects: none

- name: `sweep_design_space`, `rank_designs`
  type: function
  file: simulations/circuit_variant_predictor.py
  purpose: composes gardner_toggle_circuit.py's promoter-strength-ratio sweep with bacterial_colony_regrowth.py's division-based damage-regrowth mechanism into one design-space grid (ratio x surviving fraction), then ranks the already-BBB-grounded promoter pairings by how little surviving fraction each needs to still clear the 70% combined-fidelity bar, to prioritize which construct to build for the wet-lab damage-regrowth test (CLAUDE.md throughline item 6). Introduces no new numeric parameters, only recombines already-cited ones
  inputs: `ratios: List[float]`, `fractions: List[float]`, `n_trials: int = 10`
  outputs: per-cell bit0/bit1/combined fidelity dict; a ranked list of ratios by min surviving fraction needed
  dependencies: `simulations.gardner_toggle_circuit.GardnerParams`, `simulations.bacterial_colony_regrowth.run_colony_trial`
  used_by: `main` (in the same file)
  side_effects: none

- name: `GardnerToggleReporterCell`, `run_persistence`, `sweep_ratio_and_noise`, `sweep_maturation_and_measurement_noise`
  type: class + functions
  file: simulations/gardner_toggle_reporter_readout.py
  purpose: same Gardner repressor ODE as `gardner_toggle_circuit.py`, read out through a two-arm GFP/RFP transcriptional reporter (maturation + growth-dilution kinetics) instead of the hypothetical repressor->ion-channel->voltage link, so `gardner_toggle_circuit.py`'s genetic/voltage fidelity table has a directly comparable reporter-fidelity column. Deliberately excludes a native-oscillation interference sweep (unlike `native_oscillation_interference.py`) because the potassium-wave mechanism acts on membrane voltage specifically and no cited source proposes it affecting transcription/translation/maturation; see file docstring for that reasoning stated in full
  inputs: `GardnerParams` (imported), `ratios/tx_noise_levels` for the main sweep, `maturation_halflife_min`/`reporter_measurement_noise_std` for the reporter-sensitivity sweep (both explicitly unmeasured placeholders, not literature values)
  outputs: genetic/reporter fidelity tables (printed)
  dependencies: `simulations.gardner_toggle_circuit.GardnerParams`
  used_by: `main` (in the same file)
  side_effects: none

- name: `phase_locked_reads`, `blind_single_reads`, `sweep_phase_lock`
  type: function
  file: simulations/phase_locked_readout.py
  purpose: tests whether timing a quick voltage read to the native oscillation's predicted zero-crossings (instead of averaging over a long window) recovers accuracy, swept across how much timing error that prediction has. Found the hopeful hypothesis mostly does NOT hold: even with perfect timing knowledge, a quick read only matches the 180min-averaging fix at the lowest tested amplitude (10mV); at 20mV+ a perfectly-timed quick read lands at ~50%, no better than a blind read, because the oscillation drags cell voltage around continuously, not just at the sample instant, so a single sample stays contaminated by residual drift regardless of when it's taken
  inputs: `amplitudes/period_hours/phase_error_levels` (reuses `eis_readout_interference.run_trial_trajectory`'s amplitude/period ranges)
  outputs: blind vs. 180min-average vs. phase-locked-at-various-timing-errors accuracy table (printed)
  dependencies: `simulations.eis_readout_interference.run_trial_trajectory/eis_style_read`, `simulations.gardner_toggle_circuit.GardnerParams`
  used_by: `main` (in the same file)
  side_effects: none

- name: `sweep_coupling_and_window`
  type: function
  file: simulations/decoupled_channel_readout.py
  purpose: models a different-channel design or a yugO-knockout strain (both reduce how much of the native oscillation reaches the engineered circuit's voltage) as a swept residual-coupling fraction (100% = today's shared-channel assumption, 0% = perfect isolation), crossed with reading-window length. Found the benefit is amplitude-dependent: at a moderate real amplitude (30mV) even a partial (10%) coupling reduction makes a fast 1-minute read work well; at the worst-case documented amplitude (70mV) only a near-complete knockout does, and the 180min-averaging fix from `eis_readout_interference.py` remains the fallback that works regardless of coupling level
  inputs: `base_amplitudes/coupling_fractions/window_minutes/period_hours` (coupling fraction is an explicitly unmeasured, swept design target, not a literature value)
  outputs: accuracy table per (base amplitude, coupling fraction, window) (printed)
  dependencies: `simulations.eis_readout_interference.run_trial_trajectory/eis_style_read`, `simulations.gardner_toggle_circuit.GardnerParams`
  used_by: `main` (in the same file)
  side_effects: none

- name: `run_colony_trial`, `sweep_surviving_fraction`
  type: function
  file: simulations/reporter_colony_regrowth.py
  purpose: combines `bacterial_colony_regrowth.py`'s division-based damage/regrowth mechanism with `gardner_toggle_reporter_readout.py`'s GFP/RFP reporter cell (instead of the plain genetic-only cell), so daughters inherit reporter pools at division the same way they already inherit u/v (concentration-matching, not the original file's own new assumption). Answers a question neither source file could alone: does the fluorescent reporter still read correctly after a colony is smashed down to a few survivors and regrows. Found reporter fidelity tracks genetic fidelity exactly (100% from 2% survivors up, 0% gap at every level tested)
  inputs: `fractions: List[float]`, `n_trials: int = 12`
  outputs: genetic vs. reporter fidelity per surviving fraction (printed)
  dependencies: `simulations.gardner_toggle_reporter_readout.GardnerToggleReporterCell`, `simulations.bacterial_colony_regrowth.DOUBLING_TIME_MIN/SETTLE_WINDOW_HOURS`, `simulations.gardner_toggle_circuit.GardnerParams`
  used_by: `main` (in the same file)
  side_effects: none

- name: `run_colony_trial`, `sweep_surviving_fraction`
  type: function
  file: simulations/voltage_colony_regrowth.py
  purpose: combines all three of `bacterial_colony_regrowth.py` (damage/regrowth), `native_oscillation_interference.py` (continuous native-oscillation interference, applied throughout growth AND settling, not just to an undisturbed cell), and `eis_readout_interference.py` (long-window vs. single-snapshot voltage readout) into one trial. Also tracks `settle_minutes_available`, since worse damage takes longer to regrow within the fixed 6h settle budget, directly competing with the time left for a long EIS-style read - a previously-untested interaction. Found V-snapshot collapses to ~50% and V-window recovers to ~100% exactly as the source files predicted separately, and the existing 6h budget leaves EXACTLY 180 minutes of settle time even at the worst damage level the model can represent (1 surviving cell), zero margin, not a comfortable cushion
  inputs: `fractions/amplitude_mv/period_hours/n_trials`
  outputs: genetic / voltage-snapshot / voltage-window / settle-minutes-available per surviving fraction (printed)
  dependencies: `simulations.gardner_toggle_circuit.GardnerParams/GardnerToggleCell`, `simulations.bacterial_colony_regrowth.DOUBLING_TIME_MIN/SETTLE_WINDOW_HOURS`, `simulations.native_oscillation_interference.ambient_oscillation_offset`, `simulations.eis_readout_interference.eis_style_read`
  used_by: `main` (in the same file)
  side_effects: none

- name: `PhaseEncodedCell`
  type: class
  file: simulations/phase_encoded_readout.py
  purpose: subclass of `GardnerToggleCell` that keeps the identical repressor ODE and noise magnitudes but changes what the membrane voltage tracks: the stored bit selects the SIGN of the cell's response to the ambient potassium oscillation (in-phase vs anti-phase) instead of a static V_HIGH/V_LOW level, so both bit values sit at the same mean voltage and absolute voltage carries no information by construction. Models Yang et al. 2020 (Cell Systems, DOI 10.1016/j.cels.2020.04.002) passive-vs-active potassium response phenomenologically, NOT their Hodgkin-Huxley equations
  inputs: `params/seed/transcriptional_noise_std/channel_noise_std/thermal_noise_std/response_fraction` (response_fraction = how much of the ambient swing the cell reproduces, unmeasured, swept by callers)
  outputs: `step_phase(t_minutes, amplitude_mv, period_hours, dt)` advances u/v via the parent then sets V from the phase model
  dependencies: `simulations.gardner_toggle_circuit.GardnerToggleCell`, `simulations.native_oscillation_interference.ambient_oscillation_offset`
  used_by: `run_phase_trial`
  side_effects: none

- name: `phase_read`, `run_phase_trial`, `run_level_trial`, `accuracy`
  type: function
  file: simulations/phase_encoded_readout.py
  purpose: head-to-head test of phase encoding (bit = the cell's phase relationship to the native oscillation, read as the sign of the correlation against a separately measured reference trace) against this project's existing level encoding, under identical conditions and with read start times spread across the oscillation period so neither scheme gets an accidentally phase-locked read. Found the predicted inversion: level encoding is 100% with no oscillation and collapses to 54-65% once it is present (reproducing `native_oscillation_interference.py`), while phase encoding fails at exactly 50% with no carrier (the control working correctly) and climbs to 99-100% at 30mV and above. Also creates a direct conflict with `decoupled_channel_readout.py`: for level encoding yugO is the problem, for phase encoding yugO is the mechanism, so the two strategies are mutually exclusive and point at different chassis strains
  inputs: `scheme/amplitude_mv/window_min/measurement_noise_std/n_trials/period_hours/response_fraction/n_start_phases` (measurement noise, window and response_fraction are all explicitly unmeasured and swept, not literature values)
  outputs: four accuracy tables (inversion, measurement-noise sweep, window-length sweep, partial-coupling sweep) (printed)
  dependencies: `simulations.gardner_toggle_circuit.GardnerParams/GardnerToggleCell`, `simulations.native_oscillation_interference.ambient_oscillation_offset`
  used_by: `main` (in the same file)
  side_effects: none
- name: `partition_value`, `run_colony_trial`, `sweep`
  type: function
  file: simulations/partition_noise_regrowth.py
  purpose: replaces `bacterial_colony_regrowth.py`'s deterministic daughter-inherits-mother's-value-exactly division with real binomial partitioning noise (Huh & Paulsson 2011, kappa=1/<X>), applied to BOTH resulting daughters at every division, not just the newly-created object. Sweeps an unmeasured molecules-per-unit conversion (this model's u/v are dimensionless, not real molecule counts) from ~1 to ~2500 effective molecules. Found the circuit's own bistability makes it robust down to ~5 molecules (99-100% recovery, matching the noise-free result), only degrading at an extreme, probably-unrealistic ~1 molecule (66-87%, worse at higher damage since more surviving-fraction-driven divisions means more compounding noisy events per lineage), and even then never collapsing to chance
  inputs: `fractions/molecules_per_unit_values/n_trials`
  outputs: genetic fidelity per (molecules_per_unit, surviving fraction) (printed)
  dependencies: `simulations.gardner_toggle_circuit.GardnerParams/GardnerToggleCell`, `simulations.bacterial_colony_regrowth.DOUBLING_TIME_MIN/SETTLE_WINDOW_HOURS`
  used_by: `main` (in the same file)
  side_effects: none

- name: `ReinforcedGardnerCell`, `run_colony_trial`, `sweep`
  type: class + functions
  file: simulations/damage_sensing_reinforcement.py
  purpose: proposes and tests a damage-triggered reinforcement circuit (modeled on the real bacterial SOS/RecA-LexA damage response, Maslowska et al. 2019) that transiently boosts whichever toggle arm currently dominates during regrowth, then relaxes at settling. Re-tests it specifically against Part 22's one documented weak point (~1-molecule partition noise, 66-87% recovery). Found a 10x promoter-strength boost during regrowth fully rescues that weak point back to 100% at every damage level tested; a 5x boost already recovers to 97-99%. A real, buildable circuit addition, not yet built or wet-lab tested
  inputs: `fractions/boost_multipliers/n_trials`
  outputs: genetic fidelity per (boost multiplier, surviving fraction) (printed)
  dependencies: `simulations.gardner_toggle_circuit.GardnerParams/GardnerToggleCell`, `simulations.bacterial_colony_regrowth.DOUBLING_TIME_MIN/SETTLE_WINDOW_HOURS`, `simulations.partition_noise_regrowth.partition_value`
  used_by: `main` (in the same file)
  side_effects: none

---

## experiments/ — runnable demonstrations and diagnostic scripts

None of these use a test framework; each is a standalone script with a
`main()` and an `if __name__ == "__main__"` block. Grouped by what they're
actually diagnosing.

- name: `main` (parameter sweep over `bit_asymmetry_root_cause.py`'s physics)
  type: function
  file: experiments/bit_asymmetry_root_cause.py
  purpose: ablates each term in the bacterial tile's update equation to root-cause why bit=0 escapes more often than bit=1; found metabolic noise's coupling to an off-center V_REST is the primary driver
  dependencies: numpy (standalone reimplementation of `BacterialTile.step`, not an import, by design, see the file's own docstring)
  used_by: none (terminal analysis); its finding is the basis for `experiments/asymmetry_structural_search.py`
  side_effects: none

- name: `simulate_escape_rate`, `measure_gap`, `main`
  type: function
  file: experiments/asymmetry_structural_search.py
  purpose: automated structural search (modeled on Lobo/Morokuma/Levin 2016's method) over 3 candidate fixes for the residual escape-rate gap `bit_asymmetry_root_cause.py` left untraced; found clip-bound symmetrization, not V_REST-recentering, closes it
  dependencies: numpy
  used_by: none (terminal analysis, documented in `docs/THIRD_PARTY_METHODS.md`)
  side_effects: none

- name: `signal`, `false_positive_threshold`, `simulate_detection_latency`, `main`
  type: function
  file: experiments/damage_detection_trigger.py
  purpose: grounds wound-signal detection latency in a real citation (depolarization detectable ~1h, causal by ~3h) instead of the flat-assumed 30min polling delay used elsewhere
  dependencies: numpy
  used_by: none (terminal analysis)
  side_effects: none

- name: `get_residual_confusion_probability`, `run_pool_chain`, `check_bit_asymmetry_over_long_runs`, `main`
  type: function
  file: experiments/handoff_pool_imperfect_healing.py
  purpose: tests whether reusing a healed tile from a finite pool (vs. an infinite supply of fresh ones) hurts fidelity; also where the bit=0/bit=1 asymmetry bug (later root-caused in `bit_asymmetry_root_cause.py`) was first found
  dependencies: `simulations.biofilm_tile_handoff.BacterialTile/TileNoise/propagate_handoff`, `analysis.hidden_state_model.fit`
  used_by: none (terminal analysis)
  side_effects: none

- name: `_make_perturbed_params`, `_settled_mean_V`, `run_trial`, `_search_direction`, `find_flip_threshold`, `main`
  type: function
  file: experiments/write_axis_gardner.py
  purpose: applies `analysis/memory_geometry.py`'s write-axis method to `GardnerToggleCell`; found the circuit's exactly-symmetric baseline is an unstable knife-edge and tasmorpho's continuous linear write-map doesn't fit this substrate's ultrasensitive digital-switch regime
  dependencies: `analysis.memory_geometry.PerturbationTrial/compute_write_axis`, `simulations.gardner_toggle_circuit.GardnerParams/GardnerToggleCell`
  used_by: none (terminal analysis)
  side_effects: none

- name: `make_gardner_reservoir`, `main`
  type: function
  file: experiments/reservoir_benchmark_gardner.py
  purpose: applies `analysis/reservoir_benchmarks.py`'s NARMA-10 benchmark to `GardnerToggleCell` as the reservoir substrate; found a single toggle circuit is a weak reservoir (~8% NRMSE improvement over predicting the mean)
  dependencies: `analysis.reservoir_benchmarks.memory_capacity/run_narma10_benchmark`, `simulations.gardner_toggle_circuit.GardnerParams/GardnerToggleCell`
  used_by: none (terminal analysis)
  side_effects: none

- name: `build_parameters`, `build_initial_values`, `run_condition`, `pattern_contrast`, `main`
  type: function
  file: experiments/field_mediated_persistence.py
  purpose: runs the vendored `third_party/electric_morphogenesis` field-mediated model (field-enabled vs. gap-junction-only) against a written bit-cluster; found gap-junction diffusion alone retained contrast better than field-mediation under untuned parameters
  dependencies: `third_party/electric_morphogenesis/cellularFieldNetwork.cellularFieldNetwork` (imported via `sys.path` manipulation, see file for the exact mechanism)
  used_by: none (terminal analysis)
  side_effects: none

- name: `ParameterSweep`
  type: class
  file: experiments/parameter_sweep.py
  purpose: systematic grid search over `PlanarianTissueModel`'s g_gap/R_mem/tau_relax to find the "sweet spot" for pattern persistence (predates the noise-floor finding that the underlying passive-persistence premise doesn't hold)
  dependencies: `simulations.bioelectric_persistence.PlanarianTissueModel`
  used_by: `run_quick_sweep`, `run_comprehensive_sweep`
  side_effects: writes plots/CSV to `analysis/`

- name: `run_quick_sweep`, `run_comprehensive_sweep`
  type: function
  file: experiments/parameter_sweep.py
  purpose: entry points running a fast or exhaustive version of the sweep
  dependencies: `ParameterSweep`
  used_by: `if __name__ == '__main__'` block
  side_effects: writes plots/CSV, prompts for confirmation on the full combinatorial sweep

- name: `PersistencePredictor`, `MLPatternOptimizer`
  type: class (nn.Module, class)
  file: experiments/ml_pattern_optimizer.py
  purpose: neural-network persistence predictor and a genetic-algorithm pattern-evolution optimizer over `PlanarianTissueModel`/`BioelectricEncoder`
  dependencies: torch, sklearn, `simulations.bioelectric_persistence.PlanarianTissueModel`, `encoder.bioelectric_encoder.BioelectricEncoder`
  used_by: `run_ml_optimization_pipeline`, `quick_ml_demo`
  side_effects: writes trained model checkpoints and plots

- name: `run_ml_optimization_pipeline`, `quick_ml_demo`
  type: function
  file: experiments/ml_pattern_optimizer.py
  purpose: full pipeline (generate training data -> train predictor -> genetic algorithm) or a small synthetic-data demo of the same
  dependencies: `MLPatternOptimizer`
  used_by: `if __name__ == '__main__'` block
  side_effects: writes plots, saves a model checkpoint, prompts for confirmation on the full pipeline

- name: `InteractiveDemo`
  type: class
  file: experiments/interactive_demo.py
  purpose: interactive live-demo interface (encode custom binary strings, simulate, visualize) built explicitly for investor/VC presentations
  dependencies: `encoder.bioelectric_encoder.BioelectricEncoder`, `simulations.bioelectric_persistence.PlanarianTissueModel`
  used_by: `quick_demo`
  side_effects: interactive stdin prompts, live matplotlib animation

- name: `quick_demo`
  type: function
  file: experiments/interactive_demo.py
  purpose: entry point for the interactive demo
  dependencies: `InteractiveDemo`
  used_by: `if __name__ == '__main__'` block
  side_effects: interactive

- name: `SingleBitTrial`, `apply_raid`, `run_monte_carlo`
  type: class/function
  file: experiments/monte_carlo_ber.py
  purpose: 1000-trial Monte Carlo bit-error-rate distribution (vs. the persistence simulator's single deterministic run), with a 3x/5x RAID redundancy model
  dependencies: numpy
  used_by: `if __name__ == '__main__'` block
  side_effects: writes plots (`_plot_ber`), prints summary (`_print_ber_summary`)

- name: `RegenerationTimingModel`, `RAIDStateSimulator`
  type: class
  file: experiments/regeneration_data_loss_window.py
  purpose: models the real biologically-grounded regeneration timeline (detection -> neoblast migration -> cell division -> re-encoding, ~24-33h vulnerable window) against Bio-RAID's abstract degradation-rate assumption
  dependencies: numpy
  used_by: `run_regeneration_analysis`
  side_effects: none

- name: `run_regeneration_analysis`
  type: function
  file: experiments/regeneration_data_loss_window.py
  purpose: entry point sweeping redundancy levels against the timing model to estimate P(data loss)
  dependencies: `RegenerationTimingModel`, `RAIDStateSimulator`
  used_by: `if __name__ == '__main__'` block
  side_effects: prints summary (`_print_final_summary`)

- name: `test_betse_installation`, `test_betsee_installation`, `explore_betse_capabilities`, `create_betse_comparison_plan`
  type: function
  file: experiments/test_betse_installation.py
  purpose: checks whether the external BETSE/BETSEE package is installed and importable; not a pytest test despite the `test_` prefix, it's a standalone installation-check script
  dependencies: `betse` (external, optional)
  used_by: `if __name__ == '__main__'` block; referenced as Step 1 in the (stale) `NEXT_STEPS.py` roadmap
  side_effects: prints to stdout

- name: `check_betse_available`, `compare_acheron_vs_betse`, `validate_parameters_from_literature`, `provide_betse_integration_roadmap`
  type: function
  file: experiments/run_betse_validation.py
  purpose: intended to validate Acheron's simplified simulator against BETSE (Levin Lab's gold-standard tool); status of whether this validation was ever actually completed is unknown from this file alone, check for BETSE output artifacts before assuming it ran
  dependencies: `betse` (external, optional)
  used_by: `if __name__ == '__main__'` block
  side_effects: prints to stdout

- name: `TileState`, `TruthSource`, `Tile`, `BioRAIDController`
  type: class (Enum, Enum, class, class)
  file: experiments/phase2_bio_raid_simulator.py
  purpose: large (4284-line) Phase 2 multi-chamber Bio-RAID simulator (3-way replication, scrubbing, donor selection, rebuild throttling). **Superseded**: `docs/INVESTOR_PITCH_PHASE2_UPDATE.md`, which this simulator supports, is marked superseded in that doc's own header (unsourced TAM/revenue figures, built on the Phase 1 persistence claim later found to be a noise artifact). Not re-verified against `docs/SCIENTIFIC_AUDIT_2026.md`'s later findings
  dependencies: `simulations.bioelectric_persistence.PlanarianTissueModel`, `encoder.bioelectric_encoder.BioelectricEncoder`
  used_by: `run_phase2_simulation`
  side_effects: writes plots/animation

- name: `run_phase2_simulation`
  type: function
  file: experiments/phase2_bio_raid_simulator.py
  purpose: entry point, `--quick` (90-day) or full (1-year) simulation
  dependencies: `BioRAIDController`
  used_by: `if __name__ == '__main__'` block
  side_effects: writes plots/animation, long-running (per its own usage docstring)

---

## tests/ — pytest unit tests (covers `analysis/` only)

- name: `test_hidden_state_model.py`, `test_memory_geometry.py`, `test_reservoir_benchmarks.py`
  type: test module (group)
  file: tests/
  purpose: unit tests for the three `analysis/` modules; `test_hidden_state_model.py` specifically cross-validates against a real run of the original tasmorpho script (hardcoded reference values from that run, not just internal self-consistency)
  dependencies: `analysis.hidden_state_model`, `analysis.memory_geometry`, `analysis.reservoir_benchmarks`, pytest
  used_by: `python -m pytest tests/`
  side_effects: none

---

## third_party/electric_morphogenesis/ — vendored code (CC BY 4.0)

Vendored from santamanicka/ElectricMorphogenesis with one deliberate bug-fix
patch (see `docs/THIRD_PARTY_METHODS.md` and this directory's own
`NOTICE.md` for the exact change and why). Treat as external code; changes
here should stay minimal and documented in `NOTICE.md`, not folded in
silently.

- name: `cellularFieldNetwork`
  type: class
  file: third_party/electric_morphogenesis/cellularFieldNetwork.py
  purpose: multicellular bioelectric network model establishing the Vmem pattern across a lattice of cells (Pai et al. 2020 / Cervera et al. 2016 equations)
  dependencies: torch, `utilities`, `geneRegulatoryNetwork` (both in this same directory)
  used_by: `experiments/field_mediated_persistence.py`
  side_effects: none confirmed from the header comment alone, verify in source before modifying

- name: `geneRegulatoryNetwork`
  type: class
  file: third_party/electric_morphogenesis/geneRegulatoryNetwork.py
  purpose: per-cell gene regulatory network model, coupled to `cellularFieldNetwork`'s Vmem
  dependencies: torch
  used_by: `cellularFieldNetwork`
  side_effects: unknown, not verified

- name: `utilities`
  type: class
  file: third_party/electric_morphogenesis/utilities.py
  purpose: shared helpers, confirmed: `computeLatticeAdjacencyMatrix` (builds a 2D lattice adjacency matrix from grid dimensions)
  dependencies: torch, numpy
  used_by: `cellularFieldNetwork`
  side_effects: none (pure computation)

---

## docs/pitch/build_deck.js — pitch deck generator (not Python)

- name: (script, no exported symbols, runs top-to-bottom)
  type: script
  file: docs/pitch/build_deck.js
  purpose: pptxgenjs source that generates `docs/pitch/Acheron_Pitch_Deck.pptx` (19 slides); see the file's own header comment for the run/QA workflow
  inputs: none (all content is hardcoded in the script)
  outputs: `Acheron_Pitch_Deck.pptx` written to the current working directory
  dependencies: `pptxgenjs` (npm, not committed, install separately)
  used_by: run manually, not imported
  side_effects: writes a `.pptx` file

---

## Root-level

- name: `NEXT_STEPS.py`
  type: script
  file: NEXT_STEPS.py
  purpose: a December-2025, BETSE-centric development roadmap printed as a formatted stdout banner. No functions/classes; predates the *B. subtilis* pivot. Stale, do not treat as the current plan, see `CLAUDE.md`'s own "Next steps" section instead
  dependencies: none
  used_by: run manually (`python NEXT_STEPS.py`)
  side_effects: prints to stdout only

---

## Validation notes (Phase 4)

- Every file path above was confirmed to exist via `find`.
- Every class/function name above was confirmed via `grep -n "^(class |def |if __name__)"` against the actual file, not guessed.
- `used_by` edges for intra-repo imports were confirmed via `grep` for `from analysis|encoder|simulations|experiments|third_party import` across the whole repo; anything marked "unknown" or "not imported elsewhere" had no matching import found, this is a real absence, not an oversight, but a fresh `grep` is one command and cheap to rerun if this file is ever suspected stale.
- `simulations/bionet_propagation.py` has no confirmed importer anywhere in the repo, it may be dead code, a possible-future-integration stub, or something only ever run standalone; flagged rather than guessed at.
- `experiments/run_betse_validation.py`'s actual completion status (did the BETSE cross-validation ever run) could not be determined from the script alone.
- No entry points, API routes, database layer, or auth exist in this repo, correctly omitted rather than invented.
- Files mapped: 44 (43 `.py` + 1 `.js`). Symbols mapped: ~130 (counting grouped "internal helpers" entries as one each).
