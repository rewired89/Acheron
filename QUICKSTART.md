# Acheron Quick Start Guide

Get up and running with bioelectric memory simulations in 5 minutes.

## Prerequisites

- Python 3.9+
- pip package manager

## Installation

```bash
# Clone repository
git clone <repository-url>
cd Acheron

# Install dependencies
pip install -r requirements.txt

# Create output directories
mkdir -p analysis hardware/output
```

## Run Your First Simulation

### 1. Single Bit Persistence Test

Test if a single bit (voltage pattern) persists for 24 hours:

```bash
python simulations/bioelectric_persistence.py
```

**What this does:**
- Creates a 50x50 grid of simulated planarian cells
- Writes a '1' bit (high voltage) to a 5x5 cluster
- Simulates 24 hours of bioelectric dynamics
- Shows whether the pattern remains distinguishable

**Expected output:**
```
BIOELECTRIC PERSISTENCE TEST
Duration: 24 hours (1440 minutes)
Initial state:
  V range: 60.00 mV
  Integrity ratio: 1.00

[Progress updates...]

Final state (after 24 hours):
  V range: 45.50 mV
  Integrity ratio: 0.76
  Pattern preserved: True
```

**Success criteria:** Integrity ratio > 0.7 means the pattern survived!

### 2. Multi-Bit Storage Demo

Test storing a binary string ("10110"):

```bash
# Edit bioelectric_persistence.py to run only demo_multi_bit_storage()
python simulations/bioelectric_persistence.py
```

**What this does:**
- Encodes "10110" as 5 separate cell clusters
- Simulates pattern diffusion via gap junctions
- Measures how well each bit is preserved

### 3. Bioelectric Encoder Demo

Learn how to translate binary data to voltage patterns:

```bash
python encoder/bioelectric_encoder.py
```

**What this does:**
- Encodes binary string "10110101" into spatial voltage pattern
- Generates optogenetic light pulse sequences
- Exports DMD (Digital Micromirror Device) control file
- Tests error correction under noise

**Outputs:**
- `analysis/encoding_demo.png` - Visualization of voltage pattern
- `hardware/dmd_pattern_test.json` - Instructions for optogenetic hardware

## Understanding the Output

### Voltage Grids

Red = High voltage (-10 mV) = Bit '1'
Blue = Low voltage (-70 mV) = Bit '0'
White = Resting potential (-50 mV)

### Integrity Ratio

```
Integrity Ratio = (Measured Voltage Range) / (Initial Voltage Range)

1.0 = Perfect preservation
0.7 = Acceptable (70% of original separation)
0.5 = Degraded but recoverable with error correction
<0.3 = Pattern lost
```

### Key Parameters You Can Tweak

**In `bioelectric_persistence.py`:**

```python
# Grid size (default: 50x50)
tissue = PlanarianTissueModel(grid_size=(100, 100))

# Time step (default: 0.1 minutes)
tissue = PlanarianTissueModel(dt=0.05)  # More accurate but slower

# Gap junction strength (default: 0.02 nS)
tissue.g_gap = 0.01  # Lower = less diffusion = better preservation

# Membrane resistance (default: 100 MΩ)
tissue.R_mem = 200.0  # Higher = more stable voltage
```

**In `bioelectric_encoder.py`:**

```python
# Redundancy (default: 9 cells per bit)
encoder = BioelectricEncoder(cells_per_bit=16)  # 4x4 cluster (more robust)

# Grid size
encoder = BioelectricEncoder(grid_size=(100, 100))  # More storage capacity
```

## Next Steps

### For Researchers
1. Read `docs/WHITEPAPER_Somatic_Morphogenetic_Memory.md`
2. Modify simulation parameters to test different tissue properties
3. Run parameter sweeps to find optimal configurations

### For Investors
1. Read `docs/INVESTOR_PITCH.md`
2. Review `docs/COMPETITIVE_ANALYSIS.md`
3. Run simulations to see the technology in action

### For Engineers
1. Explore `encoder/bioelectric_encoder.py` - this is the licensable IP
2. Check `hardware/` directory for DMD control specs
3. Review optogenetic pulse sequences in encoder output

## Troubleshooting

**Simulation runs slowly:**
- Decrease grid size: `PlanarianTissueModel(grid_size=(25, 25))`
- Increase time step: `PlanarianTissueModel(dt=1.0)`
- Reduce simulation duration: `run_persistence_test(duration_hours=6)`

**Patterns don't persist:**
- Increase membrane resistance: `tissue.R_mem = 200.0`
- Decrease gap junction coupling: `tissue.g_gap = 0.01`
- Increase relaxation time constant: `tissue.tau_relax = 120.0`

**Import errors:**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.9+)

## File Structure

```
Acheron/
├── README.md                    # Project overview
├── QUICKSTART.md               # This file
├── requirements.txt            # Python dependencies
├── simulations/
│   └── bioelectric_persistence.py   # Core simulator
├── encoder/
│   └── bioelectric_encoder.py       # Binary ↔ bioelectric translator
├── hardware/
│   └── dmd_pattern_test.json       # Example optogenetic control
├── docs/
│   ├── COMPETITIVE_ANALYSIS.md     # Market research
│   ├── WHITEPAPER_Somatic_Morphogenetic_Memory.md
│   └── INVESTOR_PITCH.md
└── analysis/                   # Output visualizations
    ├── bit_initial.png
    ├── bit_final.png
    └── bit_integrity.png
```

## Key Concepts (5-Minute Primer)

### What is Bioelectric Memory?

Cells maintain voltage across their membrane (like a battery). By controlling this voltage in groups of cells, we can store information.

**Traditional computing**: 5V = '1', 0V = '0'
**Bioelectric computing**: -10mV = '1', -70mV = '0'

### Why Planarians?

Planarian flatworms can regenerate entire bodies from tissue fragments. They store their "body plan" as bioelectric voltage patterns - this same mechanism can store arbitrary data.

### The Innovation

**Current biocomputers** (Cortical Labs, Koniku) use neurons:
- Neurons = volatile memory (like RAM)
- Must be powered constantly
- Die after 6 months

**Acheron** uses planarian somatic cells:
- Somatic cells = persistent memory (like hard drive)
- Stable without power
- Regenerate if damaged

### The Market Gap

**No one sells the software to encode/decode bioelectric patterns.**

Every wetware company needs this. Our encoder works with neurons OR planarian cells. This is the licensing opportunity.

## Demo for Investors/Partners

Run this complete demo in one command:

```bash
# Run both persistence and encoding demos
python -c "
from simulations.bioelectric_persistence import demo_single_bit_storage, demo_multi_bit_storage
from encoder.bioelectric_encoder import demo_encoder

demo_single_bit_storage()
demo_multi_bit_storage()
demo_encoder()
"
```

This will:
1. Prove 24-hour pattern persistence ✓
2. Demonstrate multi-bit storage ✓
3. Show encoding/decoding pipeline ✓
4. Generate all visualizations ✓

**Runtime:** ~5-10 minutes (depending on your CPU)

## Questions?

- Technical: See `docs/WHITEPAPER_Somatic_Morphogenetic_Memory.md`
- Business: See `docs/INVESTOR_PITCH.md`
- Competition: See `docs/COMPETITIVE_ANALYSIS.md`

---

**Remember:** The goal isn't to match silicon speed - it's to create self-healing, persistent, extreme-environment bioelectric memory that nothing else can provide.
