"""
Acheron Bacterial Toggle-Switch Encoder
=========================================

Sibling to bioelectric_encoder.py, NOT a replacement. That file targets the
original planarian / optogenetic-DMD write pathway, and every assumption,
simulation, and design decision in it stays exactly as it is. Planarians
remain the target substrate for Acheron's long-term vision (regeneration,
extreme-environment tolerance); this file exists because the tooling and
literature to actually TEST the core bistable-memory claim are far more
mature in bacteria, so it's the fastest, cheapest way to find out whether
the underlying idea is real before spending planarian-scale time and money
on it.

Both pathways store the same idea: binary data as a stable, two-state
pattern in living cells. They differ in medium, write mechanism, and read
mechanism:

                        PLANARIAN PATHWAY               BACTERIAL PATHWAY (this file)
    Medium              tissue voltage gradient          genetic toggle switch (Gardner topology)
    Write               optogenetic light (DMD)          chemical/thermal induction pulse
    Read                voltage-sensitive dye imaging     reporter assay (lacZ / luminescence)
    Unit of storage      cell cluster in a 2D tissue grid  individual colony / tile

Architecture:
    Binary string -> per-colony target state -> induction protocol (JSON,
    usable directly as a bench instruction sheet) -> [wet lab happens here] ->
    reporter readout -> decode back to binary string

This targets the same circuit already designed and simulated in
simulations/gardner_toggle_circuit.py (Gardner et al. 2000 topology, built
from Bacillus BioBrick Box parts) and the same multi-colony handoff model in
simulations/biofilm_tile_handoff.py - this is the software layer sitting on
top of that already-validated design, not a new, disconnected assumption.
"""

import json
from typing import Dict, List


class BacterialToggleEncoder:
    """
    Encodes binary data as a set of per-colony bistable states in a
    B. subtilis toggle-switch circuit.

    Design principles carried over from the planarian encoder:
    1. Redundancy: each bit can be stored in multiple independent colonies
    2. Addressability: each bit maps to specific, uniquely-labeled colonies
    3. Scalability: capacity is just "how many colonies you're willing to
       grow and track" - no 2D spatial packing constraint like tissue

    IMPORTANT (see Part 8 of docs/SCIENTIFIC_AUDIT_2026.md): redundancy only
    helps once each individual colony's reading already beats chance. It
    cannot rescue a circuit that isn't holding state at all. Keep
    replication=1 until Stage 0 (bistability confirmation) has passed.
    """

    STATE_1 = "induced"     # colony pushed toward the "1" attractor
    STATE_0 = "uninduced"   # colony left at / pushed toward the "0" attractor

    def __init__(self, replication: int = 1):
        """
        Args:
            replication: colonies per bit. 1 = no redundancy (correct default
                         until the circuit itself is confirmed bistable).
                         3+ = Bio-RAID-style majority vote, meaningful only
                         AFTER Stage 0 passes.
        """
        self.replication = replication

    def binary_string_to_colony_map(self, binary_str: str) -> Dict[int, List[str]]:
        """Assign each bit to `replication` uniquely-labeled colonies.

        Returns: {bit_index: [colony_id, colony_id, ...]}
        """
        return {
            bit_idx: [f"bit{bit_idx:04d}_rep{r}" for r in range(self.replication)]
            for bit_idx in range(len(binary_str))
        }

    def encode(self, binary_str: str) -> Dict[str, str]:
        """Binary string -> {colony_id: target_state}."""
        colony_map = self.binary_string_to_colony_map(binary_str)
        target_states = {}
        for bit_idx, bit_char in enumerate(binary_str):
            target = self.STATE_1 if bit_char == '1' else self.STATE_0
            for colony_id in colony_map[bit_idx]:
                target_states[colony_id] = target
        return target_states

    def generate_induction_protocol(self, binary_str: str) -> List[Dict]:
        """
        Binary string -> a literal bench protocol: which colony gets which
        inducer pulse. Chemical induction (Gardner et al. 2000-style), not
        optogenetic DMD patterning like the planarian pathway - this is the
        bacterial equivalent of generate_optogenetic_sequence() in
        bioelectric_encoder.py.

        Inducer/concentration values reflect the PxylA/XylR arm from the
        Bacillus BioBrick Box (xylose de-represses PxylA). Confirm exact
        concentration and timing empirically in Stage 0 - these are starting
        points from the literature, not measured values.
        """
        target_states = self.encode(binary_str)
        protocol = []
        for colony_id, state in target_states.items():
            if state == self.STATE_1:
                step = {
                    'colony_id': colony_id,
                    'target_state': '1',
                    'inducer': 'xylose',
                    'concentration': '0.5% w/v',
                    'duration_min': 30,
                    'note': ('Transient pulse only, remove inducer after duration. '
                             'A correctly bistable circuit should HOLD state on its '
                             'own afterward; if it reverts once the inducer is '
                             'removed, that is itself informative (Stage 0 failing).'),
                }
            else:
                step = {
                    'colony_id': colony_id,
                    'target_state': '0',
                    'inducer': 'none',
                    'concentration': None,
                    'duration_min': 0,
                    'note': 'Default/uninduced state, no pulse needed.',
                }
            protocol.append(step)
        return protocol

    def export_induction_protocol(self, binary_str: str, output_path: str) -> Dict:
        """
        Export the induction protocol as JSON, directly usable as a lab
        bench sheet. Same role as export_dmd_pattern() in the planarian
        encoder.
        """
        protocol = self.generate_induction_protocol(binary_str)
        config = {
            'metadata': {
                'binary_data': binary_str,
                'n_bits': len(binary_str),
                'replication': self.replication,
                'n_colonies': len(protocol),
            },
            'circuit': {
                'topology': 'Gardner mutual-repression toggle switch',
                'chassis': 'Bacillus subtilis',
                'parts_source': 'Bacillus BioBrick Box (Radeck et al. 2013/2017)',
                'reference': 'simulations/gardner_toggle_circuit.py',
            },
            'induction_protocol': protocol,
        }
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Induction protocol exported to {output_path}")
        return config

    def decode(self, reporter_readings: Dict[str, float], binary_length: int,
               threshold: float = 0.5) -> str:
        """
        Reporter signal -> binary string.

        Args:
            reporter_readings: {colony_id: normalized reporter signal, 0 to 1}
                               (e.g. luminescence or color intensity, scaled
                               so 0 = fully uninduced, 1 = fully induced)
            binary_length: expected number of bits
            threshold: decision boundary (default: midpoint)

        Majority vote across replicated colonies per bit, same redundancy
        principle as the planarian decoder's cluster averaging. Per Part 8
        of the scientific audit: this only helps once each individual
        colony's reading already beats chance - it cannot manufacture
        signal that isn't there.
        """
        colony_map = self.binary_string_to_colony_map('0' * binary_length)
        decoded_bits = []
        for bit_idx in range(binary_length):
            colony_ids = colony_map[bit_idx]
            votes = [reporter_readings.get(cid, 0.0) > threshold for cid in colony_ids]
            bit = '1' if sum(votes) > len(votes) / 2 else '0'
            decoded_bits.append(bit)
        return ''.join(decoded_bits)

    def calculate_bit_error_rate(self, original: str, decoded: str) -> float:
        """Fraction of bits that decoded incorrectly."""
        if len(original) != len(decoded):
            raise ValueError("Strings must be same length")
        errors = sum(o != d for o, d in zip(original, decoded))
        return errors / len(original)


def demo_encoder():
    """
    Demo pipeline: encode -> run each colony through the ALREADY-VALIDATED
    circuit model from simulations/gardner_toggle_circuit.py -> decode ->
    measure error rate.

    This deliberately reuses that model rather than inventing new physics
    here, so the encoder/decoder is being tested against the same circuit
    the wet-lab experiment itself is designed around. Swapping the
    simulated GardnerToggleCell.step() loop for a real reporter-assay
    measurement is the only change needed to run this against real data.
    """
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'simulations'))
    from gardner_toggle_circuit import GardnerParams, GardnerToggleCell

    print("\n" + "=" * 70)
    print("BACTERIAL TOGGLE ENCODER DEMO")
    print("=" * 70 + "\n")

    encoder = BacterialToggleEncoder(replication=1)
    test_data = "10110101"
    print(f"Encoding binary string: '{test_data}'")

    protocol = encoder.generate_induction_protocol(test_data)
    plural = 'y' if encoder.replication == 1 else 'ies'
    print(f"Generated {len(protocol)}-step induction protocol "
          f"({encoder.replication} colon{plural} per bit)\n")

    # Matched-strength promoters (the Part 9 finding: mismatch destroys
    # bistability entirely rather than degrading it).
    params = GardnerParams()
    reporter_readings = {}
    for step in protocol:
        cell = GardnerToggleCell(params, seed=hash(step['colony_id']) % (2 ** 31),
                                  transcriptional_noise_std=3.0)
        cell.write(int(step['target_state']))
        n_steps = int(24 * 60 / 1.0)
        for _ in range(n_steps):
            cell.step(dt=0.02)
        # Reporter signal proxy: is the "1" repressor dominant?
        reporter_readings[step['colony_id']] = 1.0 if cell.read_genetic() == 1 else 0.0

    decoded = encoder.decode(reporter_readings, len(test_data))
    error_rate = encoder.calculate_bit_error_rate(test_data, decoded)

    print(f"Original:   '{test_data}'")
    print(f"Decoded:    '{decoded}'")
    print(f"Error rate: {error_rate:.2%}\n")
    print("This runs the SAME circuit model already used to design the")
    print("wet-lab experiment. A real lab run replaces the simulated")
    print("GardnerToggleCell.step() loop with an actual reporter-assay")
    print("measurement - nothing else in this pipeline needs to change.")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    demo_encoder()
