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

REAL NUMBERS FOUND (update, follow-up literature search):
No B. subtilis-specific, or Hernday-pap-switch-specific, per-division
fidelity number exists in the literature. What DOES exist, from a different
but mechanistically related system (mammalian CpG maintenance methylation,
read out molecule-by-molecule instead of bulk):

  - Laird, Pleasant, Clark, Sneeden, Hassan, Manley, Vary, Morgan, Hansen &
    Stoger (2004), "Hairpin-bisulfite PCR: assessing epigenetic methylation
    patterns on complementary strands of individual DNA molecules," PNAS
    101(1):204-9, DOI 10.1073/pnas.2536758100, PMC314163. Measured
    maintenance methylation efficiency directly (not inferred) on single
    DNA molecules: ~0.96 per site per cell division for a hypermethylated
    CpG island (FMR1, human lymphocytes). De novo (spurious) methylation of
    an already-unmethylated site was rarer: 0.17/division for a
    hypermethylated-context island, <0.01/division for a hypomethylated one.

  - Watanabe, Okochi-Takada, Yagi, Furuta & Ushijima (2006), "Decreased
    fidelity in replicating DNA methylation patterns in cancer cells leads
    to dense methylation of a CpG island," Curr Top Microbiol Immunol
    310:199-210, DOI 10.1007/3-540-31181-5_10. Measured fidelity in
    non-cancer (CIMP-negative) human cell lines by clonal expansion (1 cell
    to 10^6) and counting deviations: error rates <1.0x10^-3 per site per
    generation (99.9-100% fidelity) for PROMOTER CpG islands specifically.
    Cancer cells with disrupted maintenance machinery were 1.6-3.2x worse.

  - Westphal, Sauvey, Champion, Ehrenreich & Finkel (2016), "Genomewide Dam
    Methylation during Long-Term Stationary Phase," mSystems 1(6),
    DOI 10.1128/mSystems.00130-16, PMC5155068. The actually-relevant
    bacterial system: E. coli Dam (GATC adenine methylation, the same
    enzyme family the Hernday pap switch depends on). No single numeric
    fidelity given, but the finding is qualitatively strong: "virtually
    all" GATC sites stay methylated across the ENTIRE bacterial life
    cycle, including death phase and long-term starvation, confirmed by
    mass spectrometry, with methylation loss actively selected against.

HONEST CAVEATS, read before trusting a number pulled from this file:
(1) The two quantified numbers (0.96, >0.999) are human/mammalian CpG
    methylation, a DIFFERENT enzyme system (Dnmt1-family) than bacterial
    Dam. (2) B. subtilis does not natively carry the Dam/Dcm system these
    numbers, or the Hernday pap switch, depend on - Dam is essentially
    restricted to E. coli and other gammaproteobacteria. Any B. subtilis
    implementation would need Dam (or an equivalent maintenance
    methyltransferase) engineered in, another dependency, not a free win.
    (3) Fidelity clearly depends on genomic/regulatory context (promoter
    vs non-promoter, hyper- vs hypomethylated baseline) - there is no
    single universal number even within one species. Given that spread,
    this file sweeps 0.96 and 0.999 as the two EMPIRICALLY-grounded
    anchors (bracketing the real measured range above) alongside the
    wider exploratory sweep, instead of asserting one true value.

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

    # 0.999 and 0.96 are the two empirically-grounded anchors (Watanabe et al.
    # 2006 promoter-CGI best case; Laird et al. 2004 measured hypermethylated
    # CpG island) - see module docstring. Both are human/mammalian CpG
    # methylation, not B. subtilis, so still bracket rather than pin down the
    # real number for THIS project's mechanism. Remaining values stay a
    # wider exploratory sweep around that anchored range.
    fidelities = [0.999, 0.96, 0.95, 0.90, 0.80, 0.60]
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
    print("\nGROUNDING: the 99.9% and 96% rows are anchored to real measured")
    print("numbers (Watanabe et al. 2006, promoter CpG islands, non-cancer cells;")
    print("Laird et al. 2004, hairpin-bisulfite PCR, single-molecule strand-pair")
    print("readout) - see module docstring for full citations. Both are")
    print("human/mammalian CpG maintenance methylation, a different enzyme")
    print("family (Dnmt1-type) than bacterial Dam, and B. subtilis does not")
    print("natively carry Dam. So these numbers bracket a plausible range for")
    print("a well-behaved maintenance-methylation system, not a measured value")
    print("for this project's actual organism or locus. The Hernday et al.")
    print("(2002) pap switch this is modeled on is real bacterial biology that")
    print("DOES perpetuate a heritable state for many generations in vivo -")
    print("but its own numeric fidelity was not reported in that paper.")
    print("=" * 78)


if __name__ == '__main__':
    main()
