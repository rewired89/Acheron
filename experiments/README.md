# Acheron Experiments

This directory contains experimental tools for bioelectric memory optimization and validation.

## Quick Start

### 1. Test BETSE Installation
```bash
python experiments/test_betse_installation.py
```
Verifies BETSE is properly installed and explains validation strategy.

### 2. Interactive Demo (For Investors)
```bash
python experiments/interactive_demo.py
```

**Features:**
- Encode custom binary strings
- Simulate 24-hour persistence
- Test decoding accuracy
- Real-time visualizations

**Quick mode** (automated testing):
```bash
python experiments/interactive_demo.py --quick
```

### 3. Parameter Sweep (Find Optimal Settings)
```bash
python experiments/parameter_sweep.py
```

**Optimizes:**
- Gap junction conductance (`g_gap`)
- Membrane resistance (`R_mem`)
- Relaxation time constant (`tau_relax`)

**Quick mode** (faster, fewer tests):
```bash
python experiments/parameter_sweep.py --quick
```

**Output:**
- `analysis/sweep_gap_junction.png`
- `analysis/sweep_membrane_resistance.png`
- `analysis/sweep_relaxation_time.png`
- `analysis/parameter_sweep_results.csv`

### 4. ML Pattern Optimizer (AI-Designed Patterns)
```bash
python experiments/ml_pattern_optimizer.py
```

**Features:**
- Neural network predicts pattern persistence (no simulation needed!)
- Genetic algorithm evolves optimal patterns
- Publishable research contribution

**Quick mode** (small dataset):
```bash
python experiments/ml_pattern_optimizer.py --quick
```

**Output:**
- `analysis/ml_training_curve.png`
- `analysis/ml_genetic_evolution.png`
- `experiments/persistence_predictor.pth` (saved model)

### 5. BETSE Validation
```bash
python experiments/run_betse_validation.py
```

Validates our simulator against gold-standard BETSE from Levin Lab.

---

## File Descriptions

| File | Purpose | Runtime | Output |
|------|---------|---------|--------|
| `test_betse_installation.py` | Check BETSE setup | <1 min | Terminal only |
| `interactive_demo.py` | Live investor demo | 2-5 min | Interactive + PNGs |
| `parameter_sweep.py` | Find optimal parameters | 10-60 min | CSV + PNGs |
| `ml_pattern_optimizer.py` | AI pattern design | 20-90 min | Model + PNGs |
| `run_betse_validation.py` | Scientific validation | Varies | Analysis report |

---

## Typical Workflows

### For Investor Presentations
```bash
# 1. Run quick demos
python experiments/interactive_demo.py --quick
python analysis/visualize_competitive_landscape.py

# 2. Show outputs in presentation
# Use generated PNG files from analysis/ folder
```

### For Grant Applications / Publications
```bash
# 1. Full parameter sweep
python experiments/parameter_sweep.py

# 2. ML optimization
python experiments/ml_pattern_optimizer.py

# 3. BETSE validation
python experiments/run_betse_validation.py

# 4. Write paper using results + figures
```

### For Patent Filing
```bash
# 1. Demonstrate optimization
python experiments/parameter_sweep.py --quick

# 2. Show ML capability (novelty)
python experiments/ml_pattern_optimizer.py --quick

# 3. Include figures in provisional patent
# Reference analysis/*.png in patent application
```

---

## Advanced Usage

### Custom Parameter Sweep
```python
from experiments.parameter_sweep import ParameterSweep

sweeper = ParameterSweep()

# Test specific values
g_gap_values = [0.01, 0.02, 0.03, 0.04, 0.05]
df = sweeper.sweep_gap_junction(g_gap_values)

# Plot results
sweeper.plot_single_sweep(df, 'g_gap', save_path='my_sweep.png')
```

### Use Trained ML Model
```python
from experiments.ml_pattern_optimizer import MLPatternOptimizer

# Load pre-trained model
optimizer = MLPatternOptimizer()
optimizer.load_model('experiments/persistence_predictor.pth')

# Predict persistence (no simulation!)
test_pattern = optimizer.encoder.encode("10110101")
predicted_score = optimizer.predict_persistence(test_pattern)
print(f"Predicted persistence: {predicted_score:.3f}")
```

### Interactive Demo with Custom Pattern
```python
from experiments.interactive_demo import InteractiveDemo

demo = InteractiveDemo()
demo.print_banner()
demo.print_capabilities()

# Encode specific pattern
voltage = demo.encode_and_visualize("11001100")

# Simulate
final_voltage = demo.simulate_persistence(voltage, "11001100", duration_hours=48)

# Decode
decoded, error_rate = demo.test_decoding(final_voltage, "11001100")
```

---

## Dependencies

Required (install via `requirements.txt`):
- numpy
- scipy
- matplotlib
- pandas
- torch (PyTorch for ML optimizer)
- scikit-learn
- seaborn
- tqdm

Optional (for BETSE validation):
- betse (requires Python ≤3.11)
- betsee (GUI for BETSE)

---

## Troubleshooting

**"BETSE not found"**
```bash
pip install betse
# Note: Requires Python 3.11 or earlier
```

**"Out of memory" during ML training**
- Reduce `n_samples` in `generate_training_data()`
- Use smaller `grid_size` (e.g., `grid_size=(20, 20)`)

**Parameter sweep takes too long**
- Use `--quick` flag
- Reduce number of test values in sweep functions
- Use coarser grid in `full_parameter_sweep(coarse=True)`

**Interactive demo won't display plots**
- Make sure matplotlib backend is set correctly
- Try: `export MPLBACKEND=TkAgg` before running
- Or run with `plt.show()` at the end

---

## Output Directory Structure

```
analysis/
├── demo_encoding.png              # Interactive demo output
├── demo_integrity.png             # Pattern persistence over time
├── sweep_gap_junction.png         # Parameter sweep results
├── sweep_membrane_resistance.png
├── sweep_relaxation_time.png
├── heatmap_gap_Rmem.png          # 2D parameter heatmaps
├── ml_training_curve.png         # ML training progress
├── ml_genetic_evolution.png      # Genetic algorithm results
└── parameter_sweep_results.csv   # Full sweep data

hardware/
└── demo_pattern.json             # DMD control file

experiments/
└── persistence_predictor.pth     # Trained ML model
```

---

### 9. Reservoir-Computing Benchmark (Does the circuit have memory capacity?)
```bash
python experiments/reservoir_benchmark_gardner.py
```
Drives `simulations/gardner_toggle_circuit.py`'s `GardnerToggleCell` with
the NARMA-10 benchmark (methodology generalized from
[NeuromorphicMyceliumChip](https://github.com/otelhan/NeuromorphicMyceliumChip),
which trained a real physical mycelium chip on the same benchmark) and
scores a ridge-regression readout. See `docs/THIRD_PARTY_METHODS.md` for
attribution and the actual result.

**Output:** `analysis/reservoir_benchmark_gardner.png`

### 10. Dominant Write-Axis Analysis (Which perturbation writes most efficiently?)
```bash
python experiments/write_axis_gardner.py
```
Computes the Q/R/K_mem write-axis geometry (methodology generalized from
[tasmorpho](https://github.com/marcelbtec/tasmorpho)) against the Gardner
toggle circuit's own perturbation parameters, plus a direct threshold-
crossing scan for this substrate's actual (bistable/digital) behavior. See
`docs/THIRD_PARTY_METHODS.md` for attribution and the actual result — it
surfaced a real design consideration about the circuit's symmetric
baseline being an unusable knife-edge for a controllable `SET_BIT`.

### 11. Field-Mediated Pattern Persistence (Does a self-generated field help, beyond gap junctions?)
```bash
python experiments/field_mediated_persistence.py
```
Runs Manicka & Levin's own published, peer-reviewed bioelectric tissue
model (vendored under `third_party/electric_morphogenesis/`, CC BY 4.0,
one documented bug-fix patch — pretrained checkpoints deliberately NOT
used, see `third_party/electric_morphogenesis/NOTICE.md`) against a
written bit-cluster pattern, comparing field-enabled vs. gap-junction-only
persistence. See `docs/THIRD_PARTY_METHODS.md` for the actual result and
why it doesn't contradict the source paper despite looking that way at
first glance.

**Output:** `analysis/field_mediated_persistence.png`

### 12. Reused-Pool Handoff + Imperfect Healing (Does "back of the line" survive many cycles?)
```bash
python experiments/handoff_pool_imperfect_healing.py
```
Extends `biofilm_tile_handoff.py`'s single-use handoff chain to a small
reused pool of tiles (a healed tile actually comes back into rotation,
not just handed off to once), and tests whether tasmorpho's real
~15% "healing isn't a clean reset" probability (imported live from the
fitted model) matters when applied to this bacterial model. It doesn't,
for a well-understood reason — but running this surfaced a bigger,
unplanned finding: the ORIGINAL mechanism's own 100%-fidelity claim only
holds at the 5-cycle test length its own `main()` uses; run longer and a
real, asymmetric spontaneous-bit-flip risk shows up. See
`docs/THIRD_PARTY_METHODS.md` for the full result and root-cause
investigation.

**Output:** `analysis/handoff_pool_imperfect_healing.png`

### 13. Bit=0/Bit=1 Asymmetry Root Cause
```bash
python experiments/bit_asymmetry_root_cause.py
```
Ablates each term in the bacterial tile's update equation to find why
bit=0 spontaneously flips roughly 2x more often than bit=1 over a long
run (found in experiment 12, above). Root cause: `V_REST` isn't
equidistant between `V_HIGH` and `V_LOW`, which asymmetrically scales the
metabolic-noise term — verified by ablation, not guessed. See
`docs/THIRD_PARTY_METHODS.md` for the full result and a proposed
(not-yet-applied) fix.

### 14. Damage-Detection Trigger (How does the system know it needs to heal?)
```bash
python experiments/damage_detection_trigger.py
```
Every other piece of the "detect damage → handoff → heal → return" cycle
has been touched by simulation except the first step. This tests whether
`regeneration_data_loss_window.py`'s assumed detection latency
(Normal(30min, 10min), modeling a fixed polling schedule) is consistent
with real wound-signal biology — grounded in real, cited timing (PMID
30799071: wound depolarization detectable within ~1h, causally
determines outcome by ~3h) combined with Acheron's own existing noise
parameters. Finding: it depends entirely on the wound-signal's magnitude,
which isn't measured yet — at full bit-range strength the current
assumption is safe (even conservative); at 10% strength, real detection
is 3.5-7x slower than assumed. The magnitude is the concrete thing
Experiment A's planned voltage-imaging protocol would need to pin down.

**Output:** `analysis/damage_detection_trigger.png`

## Research Contributions

These experiments enable multiple publishable contributions:

1. **"Bioelectric Data Storage in Planarian Somatic Cells"**
   - Use: `bioelectric_persistence.py` + `parameter_sweep.py`
   - Venue: Nature Biomedical Engineering, Science Robotics

2. **"Machine Learning Optimization of Bioelectric Memory Patterns"**
   - Use: `ml_pattern_optimizer.py`
   - Venue: NeurIPS, ICML (bio-inspired computing track)

3. **"Persistent Information Storage in Non-Neural Bioelectric Networks"**
   - Use: Full suite + BETSE validation
   - Venue: Cell, PNAS

---

## Citation

If you use these tools in research, please cite:

```
Acheron Bioelectric Memory Project (2025)
https://github.com/[your-repo]/Acheron
```

---

## Support

For questions or issues:
- See main README.md
- Check docs/WHITEPAPER_Somatic_Morphogenetic_Memory.md
- Open GitHub issue

---

**Remember:** These are research tools. For production use, validate with wet-lab experiments at Tufts/Wyss or equivalent bioelectric research facility.
