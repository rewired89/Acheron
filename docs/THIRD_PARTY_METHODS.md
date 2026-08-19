# Third-Party Methods

This document tracks methodology reused from other projects, per the
project's no-numeric-invention rule: anything grounded in someone else's
published work must be traceable back to it.

Nothing in `analysis/reservoir_benchmarks.py`, `analysis/memory_geometry.py`,
or `analysis/hidden_state_model.py` is copied source code — the two source
repositories are either hardware/GUI-coupled (not reusable as a library) or
short enough that an independent, cited reimplementation was cleaner than a
dependency. Where a reimplementation reproduces a source project's own
numeric result as a validation check, that check is documented below with
the actual comparison, not just a claim that it matches.

## tasmorpho (Marcel Blattner, 2026)

- **Paper**: "Hidden regenerative state in planarians: A geometric model of
  bioelectric memory using Tangential Action Spaces," bioRxiv 2026,
  DOI [10.64898/2026.04.01.715890](https://doi.org/10.64898/2026.04.01.715890)
- **Code**: [github.com/marcelbtec/tasmorpho](https://github.com/marcelbtec/tasmorpho), MIT license
- **Used in**:
  - `analysis/memory_geometry.py` — the Q/R/K_mem write-axis method
    (tasmorpho script `01_betse_local_grounding.py`), generalized from a
    BETSE-specific implementation to accept perturbation trials from any
    substrate.
  - `analysis/hidden_state_model.py` — the four-parameter probit
    latent-threshold model of hidden regenerative memory (tasmorpho script
    `03_reduced_count_fit.py`), reimplemented independently but using the
    **same published phenotype counts** as reconstructed by Blattner (2026)
    from the underlying experimental papers.
- **Validation**: `03_reduced_count_fit.py` was run unmodified in this
  environment; this repo's `analysis/hidden_state_model.py` reproduces its
  point estimates and held-out predictions to 6 decimal places (see
  `tests/test_hidden_state_model.py`, which hardcodes the actual printed
  output of that run as the reference values).
- **Demonstrated in**: `experiments/write_axis_gardner.py`, applied to
  `simulations/gardner_toggle_circuit.py`'s `GardnerToggleCell` instead of
  a BETSE tissue model.

## NeuromorphicMyceliumChip (Ozgur Telhan et al.)

- **Paper**: "Morphologically Tunable Mycelium Chips for Physical Reservoir
  Computing," bioRxiv 2025.08.20.671348; also published as *Scientific
  Reports* (2026), DOI 10.1038/s41598-026-55550-5
- **Code**: [github.com/otelhan/NeuromorphicMyceliumChip](https://github.com/otelhan/NeuromorphicMyceliumChip), MIT license
- **Used in**: `analysis/reservoir_benchmarks.py` — the NARMA-10 sequence
  generator (matching their `mycelium_narma10.py:generate_narma10_data`
  formula), a ridge-regression readout, and correlation-based memory-
  capacity analysis (matching their `mycelium_memory_test.py` methodology).
  Their own implementation is a PyQt5 desktop app tightly coupled to
  Digilent hardware I/O, so it was reimplemented as a substrate-agnostic
  library rather than vendored.
- NARMA-10 itself is a standard reservoir-computing benchmark (Atiya &
  Parlos, 2000), not proprietary to either project.
- **Demonstrated in**: `experiments/reservoir_benchmark_gardner.py`,
  applied to `GardnerToggleCell` as the substrate under test.

## What running these against Acheron's own simulations found

Both demonstration experiments are real runs, not illustrative stubs —
see each script's own INTERPRETATION section for the actual numeric
result and how to reproduce it. Headline findings as of the runs recorded
in this repository's commit history:

- `experiments/reservoir_benchmark_gardner.py`: a single Gardner toggle
  circuit is a weak reservoir (~8% NRMSE improvement over predicting the
  mean on NARMA-10; a fair driving scheme matters — a naive one-sided
  drive is degenerate and must be ruled out first, see the script's own
  docstring for how that was caught).
- `experiments/write_axis_gardner.py`: the circuit's exactly-symmetric
  baseline configuration is an unstable knife-edge — a perturbation as
  small as 1e-6 (of a parameter around magnitude 50) fully determines the
  24-hour outcome. tasmorpho's continuous linear write-map framework
  doesn't fit a Hill-cooperativity-2 toggle switch (Gardner's own
  ultrasensitive digital-switch regime); a direct threshold-crossing scan
  is the correctly-posed alternative for this substrate class, and it
  surfaced a real design consideration: an exactly-symmetric design is not
  a controllable `SET_BIT` baseline without either deliberate asymmetry or
  an explicit write pulse.
