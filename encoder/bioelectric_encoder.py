"""
Acheron Bioelectric Pattern Encoder
====================================

Translates binary data into spatial bioelectric voltage patterns that can be
written to planarian tissue using optogenetic stimulation.

This is the KEY INNOVATION: The software layer that no other biocomputing
company has built. This encoder can be licensed to:
- Cortical Labs (CL-1)
- Koniku (Konikore)
- FinalSpark
- Any future wetware company

Architecture:
    Binary String → Spatial Pattern → Light Pulse Sequence → Voltage Pattern
    "10110"       → (x,y) coords    → DMD control      → Cell depolarization
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import json


class BioelectricEncoder:
    """
    Encodes binary data into bioelectric voltage patterns.

    Design Principles:
    1. Error Correction: Use redundancy (multiple cells per bit)
    2. Isolation: Spatial separation prevents crosstalk
    3. Addressability: Each bit has unique (x,y) coordinates
    4. Scalability: Grid can expand for more data
    """

    def __init__(self, grid_size=(50, 50), cells_per_bit=9):
        """
        Initialize encoder.

        Args:
            grid_size: (rows, cols) of available tissue
            cells_per_bit: How many cells encode 1 bit (redundancy)
        """
        self.rows, self.cols = grid_size
        self.cells_per_bit = cells_per_bit

        # Voltage levels (planarian-specific)
        # OPTIMIZED: Increased voltage separation for better bit stability
        self.V_high = -10.0  # mV - depolarized ("1")
        self.V_low = -80.0   # mV - hyperpolarized ("0") - OPTIMIZED from -70
        self.V_rest = -50.0  # mV - resting state

        # Calculate bit layout
        self.bits_per_row = self._calculate_bits_per_row()
        self.max_bits = self._calculate_max_bits()

    def _calculate_bits_per_row(self):
        """
        How many bits can fit in one row with proper spacing?
        """
        cluster_size = int(np.sqrt(self.cells_per_bit))
        spacing = cluster_size + 2  # 2-cell gap between clusters
        bits_per_row = self.cols // spacing
        return bits_per_row

    def _calculate_max_bits(self):
        """
        Total storage capacity of this tissue.
        """
        cluster_size = int(np.sqrt(self.cells_per_bit))
        spacing = cluster_size + 2
        bits_per_col = self.rows // spacing
        return self.bits_per_row * bits_per_col

    def binary_string_to_coords(self, binary_str: str) -> Dict[int, List[Tuple[int, int]]]:
        """
        Convert binary string to cell coordinates for each bit.

        Args:
            binary_str: String of '0' and '1' (e.g., "10110101")

        Returns:
            Dictionary mapping bit_index → list of (row, col) coordinates
        """
        if len(binary_str) > self.max_bits:
            raise ValueError(f"Binary string too long! Max {self.max_bits} bits, "
                           f"got {len(binary_str)}")

        cluster_size = int(np.sqrt(self.cells_per_bit))
        spacing = cluster_size + 2

        bit_coords = {}

        for bit_idx, bit_char in enumerate(binary_str):
            # Calculate cluster position
            row_idx = (bit_idx // self.bits_per_row) * spacing + 2
            col_idx = (bit_idx % self.bits_per_row) * spacing + 2

            # Generate all cell coordinates in this cluster
            coords = [
                (row_idx + dr, col_idx + dc)
                for dr in range(cluster_size)
                for dc in range(cluster_size)
            ]

            bit_coords[bit_idx] = coords

        return bit_coords

    def encode(self, binary_str: str) -> np.ndarray:
        """
        Encode binary string into voltage pattern grid.

        Args:
            binary_str: Binary data to encode

        Returns:
            2D numpy array of target voltages (mV)
        """
        # Initialize grid to resting potential
        voltage_grid = np.ones((self.rows, self.cols)) * self.V_rest

        # Get bit coordinates
        bit_coords = self.binary_string_to_coords(binary_str)

        # Write each bit
        for bit_idx, bit_char in enumerate(binary_str):
            target_voltage = self.V_high if bit_char == '1' else self.V_low
            coords = bit_coords[bit_idx]

            for row, col in coords:
                voltage_grid[row, col] = target_voltage

        return voltage_grid

    def decode(self, voltage_grid: np.ndarray, binary_length: int) -> str:
        """
        Read back binary string from voltage pattern.

        Args:
            voltage_grid: Measured voltage pattern
            binary_length: Expected number of bits

        Returns:
            Decoded binary string
        """
        bit_coords = self.binary_string_to_coords('0' * binary_length)
        decoded_bits = []

        # Threshold for bit decision (midpoint between high and low)
        threshold = (self.V_high + self.V_low) / 2

        for bit_idx in range(binary_length):
            coords = bit_coords[bit_idx]

            # Average voltage across all cells in cluster (error correction)
            voltages = [voltage_grid[row, col] for row, col in coords]
            avg_voltage = np.mean(voltages)

            # Decode bit
            bit = '1' if avg_voltage > threshold else '0'
            decoded_bits.append(bit)

        return ''.join(decoded_bits)

    def calculate_bit_error_rate(self, original: str, decoded: str) -> float:
        """
        Calculate how many bits were corrupted.

        Args:
            original: Original binary string
            decoded: Decoded binary string

        Returns:
            Error rate (0.0 = perfect, 1.0 = all wrong)
        """
        if len(original) != len(decoded):
            raise ValueError("Strings must be same length")

        errors = sum(o != d for o, d in zip(original, decoded))
        return errors / len(original)

    def visualize_encoding(self, binary_str: str, save_path=None):
        """
        Visualize how binary data maps to spatial voltage pattern.
        """
        voltage_grid = self.encode(binary_str)

        fig, ax = plt.subplots(figsize=(12, 10))

        im = ax.imshow(voltage_grid, cmap='RdBu_r', interpolation='nearest',
                      vmin=self.V_low - 10, vmax=self.V_high + 10)

        ax.set_title(f'Bioelectric Encoding: "{binary_str}"',
                    fontsize=16, fontweight='bold')
        ax.set_xlabel('Cell Column')
        ax.set_ylabel('Cell Row')

        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Target Voltage (mV)', rotation=270, labelpad=20)

        # Annotate each bit
        bit_coords = self.binary_string_to_coords(binary_str)
        for bit_idx, coords in bit_coords.items():
            center_row = np.mean([r for r, c in coords])
            center_col = np.mean([c for r, c in coords])

            bit_value = binary_str[bit_idx]
            color = 'white' if bit_value == '1' else 'black'

            ax.text(center_col, center_row, bit_value,
                   color=color, fontsize=14, fontweight='bold',
                   ha='center', va='center',
                   bbox=dict(boxstyle='circle', facecolor='gray', alpha=0.5))

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved encoding visualization to {save_path}")

        plt.tight_layout()
        return fig

    def generate_optogenetic_sequence(self, binary_str: str) -> List[Dict]:
        """
        Generate light pulse sequence for optogenetic writing.

        This would control a DMD (Digital Micromirror Device) to selectively
        depolarize cells using channelrhodopsin or similar light-gated channels.

        Args:
            binary_str: Binary data to write

        Returns:
            List of light pulse instructions
        """
        bit_coords = self.binary_string_to_coords(binary_str)
        pulse_sequence = []

        for bit_idx, bit_char in enumerate(binary_str):
            if bit_char == '1':
                # Only need to write '1' bits (depolarize)
                # '0' bits can use different wavelength or inhibitory opsin
                coords = bit_coords[bit_idx]

                pulse = {
                    'bit_index': bit_idx,
                    'target_voltage': self.V_high,
                    'coordinates': coords,
                    'wavelength': 470,  # nm (blue light for ChR2)
                    'intensity': 10,     # mW/mm²
                    'duration': 100,     # ms
                    'pulse_train': {
                        'frequency': 20,  # Hz
                        'n_pulses': 5
                    }
                }
            else:
                # Hyperpolarize for '0' bits
                coords = bit_coords[bit_idx]

                pulse = {
                    'bit_index': bit_idx,
                    'target_voltage': self.V_low,
                    'coordinates': coords,
                    'wavelength': 590,  # nm (yellow light for halorhodopsin)
                    'intensity': 8,      # mW/mm²
                    'duration': 150,     # ms
                    'pulse_train': {
                        'frequency': 10,  # Hz
                        'n_pulses': 3
                    }
                }

            pulse_sequence.append(pulse)

        return pulse_sequence

    def export_dmd_pattern(self, binary_str: str, output_path: str):
        """
        Export spatial pattern as DMD control file.

        DMD (Digital Micromirror Device) is the hardware that projects
        light patterns onto the tissue.

        Args:
            binary_str: Binary data to encode
            output_path: Where to save DMD instructions (JSON)
        """
        pulse_sequence = self.generate_optogenetic_sequence(binary_str)

        dmd_config = {
            'metadata': {
                'binary_data': binary_str,
                'n_bits': len(binary_str),
                'grid_size': [self.rows, self.cols],
                'cells_per_bit': self.cells_per_bit
            },
            'voltage_levels': {
                'V_high': self.V_high,
                'V_low': self.V_low,
                'V_rest': self.V_rest
            },
            'pulse_sequence': pulse_sequence
        }

        with open(output_path, 'w') as f:
            json.dump(dmd_config, f, indent=2)

        print(f"DMD pattern exported to {output_path}")
        return dmd_config


def demo_encoder():
    """
    Demonstrate encoding/decoding pipeline.
    """
    print("\n" + "="*70)
    print("BIOELECTRIC ENCODER DEMO")
    print("="*70 + "\n")

    # Create encoder
    encoder = BioelectricEncoder(grid_size=(50, 50), cells_per_bit=9)

    print(f"Encoder Configuration:")
    print(f"  Grid size: {encoder.rows} x {encoder.cols} cells")
    print(f"  Cells per bit: {encoder.cells_per_bit}")
    print(f"  Bits per row: {encoder.bits_per_row}")
    print(f"  Max storage: {encoder.max_bits} bits")
    print()

    # Test with binary string
    test_data = "10110101"
    print(f"Encoding binary string: '{test_data}'")
    print()

    # Encode
    voltage_grid = encoder.encode(test_data)
    print(f"✓ Encoded to {voltage_grid.shape} voltage grid")

    # Visualize
    encoder.visualize_encoding(test_data, save_path='analysis/encoding_demo.png')
    print(f"✓ Visualization saved")

    # Generate optogenetic sequence
    pulse_seq = encoder.generate_optogenetic_sequence(test_data)
    print(f"✓ Generated {len(pulse_seq)} optogenetic pulses")

    # Export DMD pattern
    encoder.export_dmd_pattern(test_data, 'hardware/dmd_pattern_test.json')
    print(f"✓ DMD pattern exported")

    # Decode (perfect scenario)
    decoded = encoder.decode(voltage_grid, len(test_data))
    print()
    print(f"Original:  '{test_data}'")
    print(f"Decoded:   '{decoded}'")
    print(f"Error rate: {encoder.calculate_bit_error_rate(test_data, decoded):.2%}")

    # Test with noise
    print("\nTesting robustness to noise...")
    noisy_grid = voltage_grid + np.random.normal(0, 5, voltage_grid.shape)  # 5mV noise
    decoded_noisy = encoder.decode(noisy_grid, len(test_data))
    error_rate = encoder.calculate_bit_error_rate(test_data, decoded_noisy)
    print(f"With 5mV noise - Error rate: {error_rate:.2%}")

    print("\n" + "="*70)
    print("ENCODER DEMO COMPLETE")
    print("="*70 + "\n")

    plt.show()


if __name__ == '__main__':
    demo_encoder()
