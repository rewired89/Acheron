# Quick Start

Everything in this repository is a simulation. Running these scripts does not
validate the science; it reproduces the modeling results that
`docs/SCIENTIFIC_AUDIT_2026.md` reports and argues about. Read the audit
alongside the output, not after it.

## Setup

```bash
pip install -r requirements.txt
```

A fresh sandbox often has nothing installed, and `numpy`, `scipy`, `matplotlib`
and `pytest` have all been missing at session start before. If the full install
is slow or fails, most of the simulations only need four packages:

```bash
pip install numpy scipy matplotlib pytest
```

There is no build step and no lint step.

## The four scripts worth running first

Run them in this order. Together they are the project's argument, including
the part where it contradicts itself.

### 1. The claim that broke

```bash
python simulations/planarian_02_noise_floor.py
```

Re-runs the original planarian passive-persistence model with realistic
biological noise added. Watch integrity fall from 100% (zero noise) to roughly
50% (realistic noise), which is a coin flip for a binary read. This is why the
project no longer leads with passive persistence. It also sweeps the strength
of an assumed bistable mechanism and finds that reliable storage needs roughly
15 to 20 times more feedback than the model calibrates as a realistic
engineered circuit. Treat that ratio as a relative benchmark, not a constant to
design against; the underlying parameter is a modeling knob with no directly
measured biological equivalent.

### 2. The circuit that replaced it

```bash
python simulations/bsubtilis_01_gardner_toggle_circuit.py
```

A Gardner-style genetic toggle switch using real *B. subtilis* BioBrick parts.
The useful output is the failure mode, not the success: mismatched promoter
strengths collapse the circuit into a single stable state, which is a dead
switch. Promoter matching is the variable Stage 0 of the roadmap exists to
test.

### 3. The differentiator

```bash
python simulations/bsubtilis_07_colony_regrowth.py
python simulations/bsubtilis_13_reporter_colony_regrowth.py
```

Damage a colony, regrow it by division, and check whether the bit is still
there. It recovers to full fidelity from as little as 2% surviving cells,
because division copies the circuit's proteins into daughters. The second
script adds a fluorescent reporter and finds it tracks the genetic state
exactly, with no extra fragility. Surviving division is the thing published
prior art cannot do, so this pair is the core of the pitch.

### 4. The readout problem

```bash
python simulations/bsubtilis_08_native_oscillation_interference.py
python simulations/bsubtilis_09_eis_readout_interference.py
python simulations/bsubtilis_18_phase_encoded_readout.py
```

*B. subtilis* biofilms run their own potassium-wave signaling. The first
script shows a single voltage snapshot taken during it collapsing to about 50%
accuracy while the underlying genetic state is perfectly intact. The second
tests averaging over a long window as a fix, and the honest result is that it
only works once the window reaches about one full oscillation period, roughly
three hours, which is far longer than a real impedance sweep takes. The third
tries the opposite framing, encoding the bit as a phase relationship to the
oscillation rather than as a voltage level, and finds the readout gets better
as the oscillation gets stronger.

Those last two point in different directions and want different chassis
strains. That fork is unresolved and is documented as unresolved. Do not read
one of the three scripts and stop.

## Other things to run

```bash
python simulations/crossorganism_01_comparison_summary.py   # ranks mechanisms by hidden wet-lab risk
python simulations/bsubtilis_15_partition_noise_regrowth.py      # uneven molecule splitting at division
python simulations/bsubtilis_16_damage_sensing_reinforcement.py  # proposed SOS-style reinforcement circuit
python simulations/bsubtilis_19_reservoir_benchmark.py   # external benchmark method against this project's circuit
python simulations/bsubtilis_05_asymmetry_structural_search.py
python -m pytest tests/                             # unit tests, cover analysis/ only
```

Most of `experiments/` works this way: a runnable script that prints its own
result, with no test framework around it. Some of the heavier scripts take
several minutes.

## Reading the output

Two numbers recur across the simulations.

**Fidelity or integrity** is the fraction of reads that return the bit that was
written. 1.0 is perfect, 0.5 is a coin flip and means the bit is gone. A result
near 0.5 is not partial success; it is total failure wearing a respectable
number.

**SNR** is the separation between the two states relative to the noise. The
project's own pass threshold, defined before the results came in, is fidelity
at or above 70% with SNR at or above 3:1.

Scripts state their own caveats in their docstrings and in their printed
output. Those caveats are load-bearing. A result reported without them is
misreported.

## Where to go next

- `docs/SCIENTIFIC_AUDIT_2026.md` is the source of truth for what is proven
  versus assumed, appended to continuously and organized in numbered parts.
- `CODEMAP.md` maps the code structure, though the source file is always
  authoritative if the two disagree.
- `docs/ACHERON_101.md` is a plain-language primer if the biology is new.
- `experiments/BENCH_PROTOCOL_BSUBTILIS.md` is the draft *B. subtilis* bench protocol.
- `docs/INVESTOR_PITCH.md` has the four-stage roadmap and its costs.
- Older documents (`docs/INVESTOR_PITCH_PHASE2_UPDATE.md`, the `PHASE2`,
  `PHASE3` and `PHASE4` files, the whitepaper) predate several corrections.
  Cross-check anything in them against the audit before reusing it.
