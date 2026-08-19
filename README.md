# Acheron: Somatic Morphogenetic Memory Chip

**Bioelectric Memory Using Planarian Cells for Extreme Environment Computing**

## Vision
Create the world's first self-healing, regenerative bioelectric memory chip using planarian somatic cells instead of neurons. Target applications: space hardware, deep-sea systems, and sovereign computing infrastructure.

## Core Differentiation

### vs. Competitors (Cortical Labs, Koniku, FinalSpark)
| Feature | Neurons (Competitors) | Planarian Cells (Acheron) |
|---------|----------------------|---------------------------|
| Memory Type | Volatile (RAM) | Persistent (Hard Drive) |
| Lifespan | 6 months - 2 years | Indefinite (regenerative) |
| Self-Healing | None | Full regeneration |
| Environment | Lab conditions only | Extreme (space, radiation) |
| Energy | High (life support) | Low (resilient metabolism) |

### The Unfilled Gap: Bioelectric Write/Read Interface
**No company currently sells software to reliably encode/decode binary data into bioelectric patterns.**
This software layer can be licensed to ALL biocomputing companies.

## Technical Approach

### Phase 1: Prove Pattern Persistence (Current)
1. **Simulation** - BETSE-based models proving voltage patterns persist 24+ hours
2. **Bio-Flip-Flop** - Demonstrate stable binary states in cell clusters
3. **White Paper** - "Somatic Memory Persistence in Planarian Bioelectric Networks"

### Phase 2: Optogenetic Write Interface
1. **Pattern Encoder** - Python code: binary string → light pulse patterns
2. **DMD Controller** - Interface to Digital Micromirror Device
3. **Verification** - Read back voltage patterns to confirm write

### Phase 3: Hardware Prototype
1. **Planarian Cell Culture** - Partner with lab (Tufts/Wyss preferred)
2. **Microfluidic Chip** - Physical substrate for cells
3. **Multi-Bit Storage** - Scale from 1 bit to 8-bit byte

## Project Structure

```
/simulations       - BETSE models and pattern persistence proofs
/encoder           - Binary → bioelectric pattern translator
/hardware          - Optogenetic controller (DMD interface)
/docs              - White papers, technical specs
/analysis          - Data visualization, comparative studies, and reusable
                      analysis methods (reservoir-computing benchmarks,
                      write-axis geometry, hidden-state modeling — see
                      docs/THIRD_PARTY_METHODS.md for what's grounded in
                      external published methodology)
/experiments        - Runnable experiment scripts, including reservoir-
                      benchmark, write-axis, and field-mediated-persistence
                      demonstrations against Acheron's own circuits
/third_party        - Vendored code from CC-BY/MIT-licensed external
                      projects, with attribution NOTICE files (see
                      docs/THIRD_PARTY_METHODS.md)
/tests              - pytest unit tests for the analysis/ modules
```

## Analysis Methods

Beyond the project's own BETSE-inspired simulations, `analysis/` and
`third_party/` include methods adapted from published external work and
validated against Acheron's own circuits (not just left as unused library
code) — see `docs/THIRD_PARTY_METHODS.md` for full attribution and the
actual findings:

| Module | Method | Source |
|---|---|---|
| `analysis/reservoir_benchmarks.py` | NARMA-10 + memory-capacity benchmark | Generalized from [NeuromorphicMyceliumChip](https://github.com/otelhan/NeuromorphicMyceliumChip) |
| `analysis/memory_geometry.py` | Q/R/K_mem dominant write-axis | Generalized from [tasmorpho](https://github.com/marcelbtec/tasmorpho) |
| `analysis/hidden_state_model.py` | Latent-threshold hidden-memory model | Reimplemented from tasmorpho, numerically validated to 6 decimal places against a real run of the original |
| `third_party/electric_morphogenesis/` | Field-mediated bioelectric tissue model | Vendored (CC BY 4.0, one bug-fix patch) from [ElectricMorphogenesis](https://github.com/santamanicka/ElectricMorphogenesis) |

Also referenced (not integrated — the source has no code license, only
the published paper is cited): T-Pro / compressed genetic circuits
(Huang et al. 2025, *Nature Communications*), a directly relevant
precedent for `gardner_toggle_circuit.py`'s open "hypothetical
ion-channel-output link" problem — see `docs/THIRD_PARTY_METHODS.md`.

Run the demonstrations:
```bash
python experiments/reservoir_benchmark_gardner.py
python experiments/write_axis_gardner.py
python experiments/field_mediated_persistence.py   # requires torch (already in requirements.txt)
python -m pytest tests/
```

## Competitive Intelligence

**Companies Using Neurons:**
- Cortical Labs: CL-1 biocomputer ($35K, 6-month neuron lifespan)
- Koniku: VOC detection (2-year neuron lifespan)
- FinalSpark: Brain organoid computing (Swiss)

**Closest Adjacent:**
- Morphoceuticals: Using Levin's bioelectric work for regenerative medicine (NOT computing)

**Our Moat:**
1. First to use planarian somatic cells for computing
2. First bioelectric pattern encoding/decoding software stack
3. Patents on planarian-based memory architecture
4. Extreme environment hardening (space/radiation certified)

## Next Steps
1. ✅ Competitive analysis
2. 🔄 BETSE simulation setup
3. ⏳ Prove 24-hour pattern persistence
4. ⏳ Draft white paper
5. ⏳ Approach Tufts/Wyss for wetware partnership

## License
Proprietary - Patent pending on Somatic Morphogenetic Memory architecture
