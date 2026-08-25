"""
Acheron Simulation 10: Methylation-Based Bit Encoding - Step 1 (Write + Hold)
================================================================================

Prompted by reading BioCompute Inc's public repos directly
(github.com/biocompute-inc) rather than relying on a secondhand description:
their actual mechanism is DNA methylation calling via Nanopore/Modkit (B2A),
not CRISPR sequence editing, which an earlier web summary had claimed. That's
a genuinely different, and for this project, interesting mechanism:
methylation is a chemical tag layered on TOP of the existing DNA sequence,
not a change to it, and cells already have native machinery (maintenance
methyltransferases) that copies methylation state onto daughter cells at
every division. Unlike Acheron's own Gardner toggle-switch, which needs
bistability engineered from scratch, epigenetic memory rides on a mechanism
the cell already runs on every division - IF it holds well enough.

REAL PRECEDENT THIS IS GROUNDED IN:
Hernday, Krabbe, Braaten & Low (2002), "Self-perpetuating epigenetic pili
switches in bacteria," PNAS 99(Suppl 4):16470-6,
DOI 10.1073/pnas.182427199, PMC139910. A real, naturally-evolved,
self-perpetuating epigenetic bistable switch in E. coli (the pap pilin
operon): two Dam methylation sites plus regulatory proteins (Lrp, PapI,
PapB, CAP) maintain a heritable ON/OFF phase state purely through the
methylation pattern surviving DNA replication. Not a designed circuit like
Gardner's - existing, evolved biology that already does what "step 1" here
needs: hold a heritable bit via methylation state.

WHAT THIS DOES NOT DO (read before citing a number from this file):
No per-division methylation-maintenance FIDELITY number specific to this
mechanism, or to B. subtilis, was found in the literature search grounding
this file. General epigenetics literature calls maintenance methylation
"high fidelity," but a specific, citable per-site-per-division error rate
for this exact system wasn't located. That number is therefore SWEPT as an
explicit unknown parameter below - same honest treatment as every other
unmeasured parameter elsewhere in this project (bistable_k, transcriptional
noise, etc.), not asserted as measured.

MODEL:
A methylation "bit" at a target locus: methylated = 1, unmethylated = 0. At
each division, the daughter's site starts hemimethylated (one strand carries
the parent's mark, the new strand doesn't); maintenance methyltransferase
then either correctly re-methylates it (probability `maintenance_fidelity`)
or fails to, flipping the bit. A simplified, single-parameter version of the
real hemimethylation mechanism Hernday et al. describe - not the full
regulatory circuit (Lrp/PapI/PapB binding kinetics), which is the natural
next refinement once this simplest version is checked.
"""

import numpy as np
from typing import Dict, List


def simulate_methylation_lineage(initial_bit: int, maintenance_fidelity: float,
                                  n_generations: int, seed: int) -> List[int]:
    """Track one cell lineage's methylation bit across n_generations of
    division. At each division the bit is correctly maintained with
    probability maintenance_fidelity, else it flips."""
    rng = np.random.default_rng(seed)
    bit = initial_bit
    history = [bit]
    for _ in range(n_generations):
        if rng.random() > maintenance_fidelity:
            bit = 1 - bit
        history.append(bit)
    return history


def population_readout(initial_bit: int, maintenance_fidelity: float,
                        n_generations: int, n_lineages: int, seed: int) -> float:
    """Simulate n_lineages independent cell lineages (a colony descending
    from one written cell) and return the fraction still holding the
    correct bit after n_generations - what a real bulk methylation-fraction
    readout (like B2A's threshold-based decode) would measure."""
    rng = np.random.default_rng(seed)
    correct = 0
    for _ in range(n_lineages):
        lineage_seed = int(rng.integers(0, 2**31))
        final_bit = simulate_methylation_lineage(initial_bit, maintenance_fidelity,
                                                   n_generations, lineage_seed)[-1]
        correct += int(final_bit == initial_bit)
    return correct / n_lineages


def sweep_fidelity(fidelities: List[float], n_generations_list: List[int],
                    n_lineages: int = 300) -> Dict:
    results = {}
    for fidelity in fidelities:
        for n_gen in n_generations_list:
            scores = []
            for bit in [0, 1]:
                seed = int(fidelity * 10000) + n_gen * 7 + bit
                scores.append(population_readout(bit, fidelity, n_gen, n_lineages, seed))
            results[(fidelity, n_gen)] = float(np.mean(scores))
    return results


def main():
    print("=" * 78)
    print("METHYLATION-BASED BIT ENCODING - Step 1: does the written bit hold?")
    print("=" * 78)
    print("\nMechanism: bit = methylated(1)/unmethylated(0) at a target locus,")
    print("maintained through division by an (unmeasured) maintenance fidelity.\n")

    fidelities = [0.999, 0.99, 0.95, 0.90, 0.80, 0.60]
    generations = [1, 5, 10, 20, 48]   # 48 gen ~= 1 day at 30-min doubling

    header = f"{'Fidelity/division':<20}" + "".join(f"{f'{g}gen':>10}" for g in generations)
    print(header)
    results = sweep_fidelity(fidelities, generations)
    for fidelity in fidelities:
        row = f"{fidelity:<20.1%}"
        for n_gen in generations:
            score = results[(fidelity, n_gen)]
            row += f"{score:>10.1%}"
        print(row)

    print("\n" + "=" * 78)
    print("INTERPRETATION")
    print("=" * 78)
    print("Error compounds ONCE PER DIVISION here, not continuously like the")
    print("bioelectric circuit's noise-floor problem - a fundamentally different")
    print("failure mode. B. subtilis doubles roughly every 30 min, so ~48")
    print("generations pass in a single day. Even a fidelity that sounds strong")
    print("in isolation can decay hard by the 48-generation column - that's the")
    print("actual number to watch, not the 1-generation column.")
    print("\nNEXT STEP (not done here): find or measure a real per-division")
    print("fidelity number for this exact mechanism before trusting any column.")
    print("The Hernday et al. (2002) system this is modeled on is real and DOES")
    print("perpetuate a heritable state in living bacteria - but this file's")
    print("fidelity axis is still an assumption, not a citation, same status as")
    print("every other unmeasured noise parameter in this project.")
    print("=" * 78)


if __name__ == '__main__':
    main()
