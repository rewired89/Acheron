# NOTICE

The three files in this directory (`cellularFieldNetwork.py`,
`geneRegulatoryNetwork.py`, `utilities.py`) are copied **unmodified** from:

- **Repository**: [github.com/santamanicka/ElectricMorphogenesis](https://github.com/santamanicka/ElectricMorphogenesis)
- **Paper**: Manicka, S., & Levin, M. (2025). "Field-mediated bioelectric
  basis of morphogenetic prepatterning." *Cell Reports Physical Science*,
  102865.
- **License**: The repository's `LICENSE` file (copied alongside, unchanged)
  is CC BY 4.0 (Creative Commons Attribution 4.0 International) — note the
  source repo's own README says "MIT License. See LICENSE for details,"
  which does not match the actual LICENSE file content. CC BY 4.0 (the
  license the file itself actually states) is treated as authoritative
  here; both permit reuse with attribution, so this doesn't change what's
  allowed, but it's worth flagging as an inconsistency in the upstream repo.

**What was deliberately left out**: the repository also ships pretrained
model checkpoints (`data/*.dat`) loaded via `torch.load(...)` without
`weights_only=True`. Those are pickled Python objects from an
unverified third party — deserializing them without `weights_only=True`
can execute arbitrary code, and the safe (`weights_only=True`) load fails
because the checkpoints bundle plain Python config objects alongside
tensors, not just tensor weights. None of that data, and none of the
driver scripts that load it (`simulateTrainedModel.py`, and the
`clampMode == 'learned'` branch of `simulateCellularFieldNetwork.py`),
were copied or used. Everything run against this code in
`experiments/field_mediated_persistence.py` uses hand-specified
parameters (adapted from the published defaults in the source repo's own
`simulateCellularFieldNetwork.py`) instead of a pretrained checkpoint —
see that experiment script for the actual values and how they were
chosen.
