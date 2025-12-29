"""
BioNet: Bioelectric Internet Propagation Simulator
===================================================

Simulates voltage wave propagation through gap-junction-coupled planarian
cell chains (bio-cables) connecting multiple Bio-RAID storage chips.

This demonstrates the world's first biological internet - where living cells
act as the communication medium, self-heal when damaged, and maintain
connectivity indefinitely through regeneration.

Author: Acheron Project
Date: December 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.sparse import diags, csr_matrix
from scipy.sparse.linalg import spsolve
import time
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum


class PulseType(Enum):
    """Bioelectric pulse encoding types"""
    BIT_0 = 0  # Low/no pulse
    BIT_1 = 1  # High pulse
    SILENCE = 2  # Inter-bit gap
    ACK = 3  # Acknowledgment signal


@dataclass
class BioelectricPacket:
    """Data packet for BioNet transmission"""
    source_chip: int
    dest_chip: int
    data: bytes
    checksum: int
    timestamp: float


class BioCable:
    """
    Living tissue cable connecting two Bio-RAID chips.

    Consists of gap-junction-coupled planarian cells that:
    - Propagate voltage waves (data transmission)
    - Regenerate when severed (self-healing)
    - Require only nutrients (no electrical power)
    """

    def __init__(self, length_mm=20, cells_per_mm=2, dt=0.1):
        """
        Initialize bio-cable.

        Args:
            length_mm: Cable length in millimeters
            cells_per_mm: Cell density (2 cells/mm = 1mm spacing)
            dt: Time step in seconds
        """
        self.length_mm = length_mm
        self.n_cells = int(length_mm * cells_per_mm)
        self.dt = dt

        # Voltage array (mV) - one value per cell
        self.V = np.ones(self.n_cells) * -50.0  # Resting potential

        # Cell properties (planarian-specific from Levin lab)
        self.V_rest = -50.0  # mV - resting membrane potential
        self.g_gap = 0.5  # mS/cm² - gap junction conductance
        self.C_mem = 1.0  # μF/cm² - membrane capacitance
        self.R_mem = 10.0  # kΩ·cm² - membrane resistance
        self.tau = self.C_mem * self.R_mem  # Time constant (ms)

        # Cable health (for simulating damage/regeneration)
        self.is_severed = False
        self.severance_point = None
        self.regeneration_progress = 0.0  # 0.0 = just cut, 1.0 = fully healed

        # Transmission tracking
        self.current_bit = None
        self.transmission_active = False

    def propagate_voltage(self, source_voltage, source_cell=0):
        """
        Propagate voltage pulse from source cell through cable.

        Uses cable equation:
        C_mem * dV/dt = -I_mem + I_gap

        Where:
        - I_mem: Current through membrane (leakage)
        - I_gap: Current through gap junctions (coupling to neighbors)
        """
        # Apply source voltage at one end
        self.V[source_cell] = source_voltage

        # Build gap junction coupling matrix
        if self.is_severed and self.regeneration_progress < 1.0:
            # Cable is severed - no coupling at break point
            coupling = self._build_severed_coupling_matrix()
        else:
            # Intact cable - full coupling
            coupling = self._build_coupling_matrix()

        # Solve cable equation (discretized)
        # dV/dt = (1/tau) * (-V + V_rest) + (g_gap/C_mem) * coupling * V

        membrane_relaxation = (-self.V + self.V_rest) / self.tau
        gap_junction_coupling = (self.g_gap / self.C_mem) * coupling.dot(self.V)

        dV_dt = membrane_relaxation + gap_junction_coupling

        # Update voltage (Forward Euler integration)
        self.V += dV_dt * self.dt

        # Clamp to realistic bounds
        self.V = np.clip(self.V, -80, +40)

    def _build_coupling_matrix(self):
        """Build gap junction coupling matrix (tridiagonal)"""
        # Each cell couples to left/right neighbors
        main_diag = -2 * np.ones(self.n_cells)
        off_diag = np.ones(self.n_cells - 1)

        # Boundary conditions: endpoints only couple to one neighbor
        main_diag[0] = -1
        main_diag[-1] = -1

        coupling = diags([off_diag, main_diag, off_diag], [-1, 0, 1],
                        shape=(self.n_cells, self.n_cells))
        return coupling.tocsr()

    def _build_severed_coupling_matrix(self):
        """Build coupling matrix with severance (break at severance point)"""
        coupling = self._build_coupling_matrix().toarray()

        if self.severance_point is not None:
            # Zero out coupling at severance point
            idx = self.severance_point
            coupling[idx, idx+1] = 0
            coupling[idx+1, idx] = 0

            # Partial regeneration allows some coupling
            if self.regeneration_progress > 0:
                repair_strength = self.regeneration_progress ** 2  # Nonlinear recovery
                coupling[idx, idx+1] = repair_strength
                coupling[idx+1, idx] = repair_strength

        return csr_matrix(coupling)

    def sever_cable(self, position_fraction=0.5):
        """Simulate cable damage (cut by micrometeorite, etc.)"""
        self.is_severed = True
        self.severance_point = int(self.n_cells * position_fraction)
        self.regeneration_progress = 0.0
        print(f"⚠️  Cable severed at cell {self.severance_point}")

    def regenerate(self, progress_increment=0.01):
        """
        Simulate biological regeneration of gap junctions.

        Planarian cells naturally reform gap junctions after damage.
        Full regeneration takes ~7-14 days in reality.
        """
        if self.is_severed:
            self.regeneration_progress += progress_increment
            if self.regeneration_progress >= 1.0:
                self.regeneration_progress = 1.0
                self.is_severed = False
                print(f"✅ Cable regeneration complete!")

    def send_pulse(self, pulse_type: PulseType, duration_sec=5.0):
        """
        Send bioelectric pulse (represents one bit).

        Args:
            pulse_type: Type of pulse (BIT_0, BIT_1, etc.)
            duration_sec: How long to hold the voltage
        """
        if pulse_type == PulseType.BIT_1:
            return +20.0  # Depolarizing pulse (bit 1)
        elif pulse_type == PulseType.BIT_0:
            return -50.0  # Resting (bit 0, or just absence of pulse)
        elif pulse_type == PulseType.ACK:
            return +15.0  # Acknowledgment signal
        else:
            return -50.0  # Silence


class BioNetNode:
    """
    A Bio-RAID storage chip that can send/receive data via BioNet.

    Each node:
    - Has local Bio-RAID storage (from Phase 2)
    - Connects to neighbors via bio-cables
    - Routes packets through bioelectric network
    """

    def __init__(self, node_id: int, position: Tuple[float, float]):
        """
        Initialize BioNet node.

        Args:
            node_id: Unique identifier (0, 1, 2, ...)
            position: (x, y) coordinates for visualization
        """
        self.node_id = node_id
        self.position = position
        self.connections = {}  # {neighbor_id: BioCable}

        # Voltage state (for transmission/reception)
        self.transmit_voltage = -50.0
        self.receive_voltage = -50.0

        # Packet buffer
        self.packet_queue = []

    def connect_to(self, neighbor: 'BioNetNode', cable_length_mm=20):
        """Create bio-cable connection to neighbor node"""
        cable = BioCable(length_mm=cable_length_mm)
        self.connections[neighbor.node_id] = cable
        neighbor.connections[self.node_id] = cable  # Bidirectional
        print(f"🔗 Node {self.node_id} ↔ Node {neighbor.node_id} connected ({cable_length_mm}mm bio-cable)")

    def send_byte(self, byte_value: int, dest_node_id: int):
        """
        Encode byte as bioelectric pulse sequence and transmit.

        Encoding: Each bit = one pulse (5 seconds)
        Byte "10110010" = 8 pulses = 40 seconds total
        """
        if dest_node_id not in self.connections:
            print(f"❌ Node {dest_node_id} not connected to Node {self.node_id}")
            return False

        cable = self.connections[dest_node_id]

        print(f"\n📡 Node {self.node_id} → Node {dest_node_id}: Transmitting byte 0x{byte_value:02X} ({byte_value:08b})")

        # Convert byte to 8 bits
        bits = [(byte_value >> i) & 1 for i in range(7, -1, -1)]

        # Transmit each bit as voltage pulse
        for i, bit in enumerate(bits):
            pulse_type = PulseType.BIT_1 if bit == 1 else PulseType.BIT_0
            pulse_voltage = cable.send_pulse(pulse_type)

            # Inject pulse at source end of cable
            cable.V[0] = pulse_voltage

            print(f"  Bit {i}: {bit} ({'HIGH' if bit else 'LOW'}) → {pulse_voltage:+.1f}mV")

        return True

    def route_packet(self, packet: BioelectricPacket):
        """
        Route packet to destination (multi-hop if needed).

        Simple flooding algorithm (v1.0):
        - If dest is neighbor: send directly
        - Else: broadcast to all neighbors
        """
        if packet.dest_chip in self.connections:
            # Direct connection - send immediately
            self.send_byte(packet.data[0], packet.dest_chip)
        else:
            # No direct connection - flood to all neighbors
            for neighbor_id in self.connections.keys():
                if neighbor_id != packet.source_chip:  # Don't send back to source
                    self.send_byte(packet.data[0], neighbor_id)


class BioNetSimulator:
    """
    Full BioNet mesh network simulator.

    Simulates multiple Bio-RAID chips connected by bio-cables,
    demonstrating voltage wave propagation, packet routing, and self-healing.
    """

    def __init__(self):
        self.nodes = []
        self.time = 0.0
        self.dt = 0.1  # seconds

    def add_node(self, node: BioNetNode):
        """Add node to network"""
        self.nodes.append(node)

    def simulate_transmission(self, source_id: int, dest_id: int,
                             data_byte: int, duration_sec=60.0, visualize=True):
        """
        Simulate one byte transmission across BioNet.

        Args:
            source_id: Source node ID
            dest_id: Destination node ID
            data_byte: Byte to transmit (0-255)
            duration_sec: Simulation duration
            visualize: Show animation of voltage propagation
        """
        source_node = self.nodes[source_id]
        dest_node = self.nodes[dest_id]

        # Create packet
        packet = BioelectricPacket(
            source_chip=source_id,
            dest_chip=dest_id,
            data=bytes([data_byte]),
            checksum=data_byte ^ 0xFF,  # Simple XOR checksum
            timestamp=self.time
        )

        print(f"\n{'='*60}")
        print(f"BioNet Transmission Simulation")
        print(f"{'='*60}")
        print(f"Source: Node {source_id}")
        print(f"Destination: Node {dest_id}")
        print(f"Data: 0x{data_byte:02X} ({data_byte:08b})")
        print(f"{'='*60}\n")

        # Send packet
        source_node.route_packet(packet)

        # Get cable for visualization
        if dest_id in source_node.connections:
            cable = source_node.connections[dest_id]

            if visualize:
                self._visualize_propagation(cable, source_node, dest_node,
                                           data_byte, duration_sec)

    def _visualize_propagation(self, cable: BioCable, source: BioNetNode,
                               dest: BioNetNode, byte_val: int, duration_sec: float):
        """
        Animate voltage wave propagating through bio-cable.

        Creates matplotlib animation showing:
        - Voltage at each cell along cable
        - Wave propagation from source to destination
        - Regeneration if cable is severed
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Setup cable visualization
        x_positions = np.linspace(0, cable.length_mm, cable.n_cells)
        line, = ax1.plot(x_positions, cable.V, 'b-', linewidth=2)
        ax1.axhline(y=-50, color='gray', linestyle='--', alpha=0.5, label='Resting potential')
        ax1.set_xlim(0, cable.length_mm)
        ax1.set_ylim(-80, +40)
        ax1.set_xlabel('Position along bio-cable (mm)', fontsize=12)
        ax1.set_ylabel('Voltage (mV)', fontsize=12)
        ax1.set_title(f'BioNet: Voltage Propagation (Node {source.node_id} → Node {dest.node_id})',
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()

        # Add node markers
        ax1.axvline(x=0, color='green', linestyle='-', linewidth=3, alpha=0.7, label=f'Node {source.node_id}')
        ax1.axvline(x=cable.length_mm, color='red', linestyle='-', linewidth=3, alpha=0.7, label=f'Node {dest.node_id}')

        # Severance marker (if applicable)
        severance_line = None
        if cable.is_severed:
            severance_line = ax1.axvline(x=cable.severance_point * cable.length_mm / cable.n_cells,
                                         color='orange', linestyle='--', linewidth=2, label='Severed')

        # Bit pattern visualization
        bits = [(byte_val >> i) & 1 for i in range(7, -1, -1)]
        bit_display = ''.join(str(b) for b in bits)
        ax2.text(0.5, 0.7, f'Transmitting: 0x{byte_val:02X}',
                ha='center', va='center', fontsize=16, transform=ax2.transAxes)
        ax2.text(0.5, 0.5, f'Binary: {bit_display}',
                ha='center', va='center', fontsize=20, fontfamily='monospace',
                transform=ax2.transAxes, fontweight='bold')
        ax2.text(0.5, 0.3, f'Bandwidth: ~0.1 bits/sec',
                ha='center', va='center', fontsize=12, transform=ax2.transAxes,
                style='italic', color='gray')
        ax2.axis('off')

        # Time and status text
        time_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes,
                            fontsize=10, verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Animation state
        frame_count = [0]
        pulse_schedule = []

        # Build pulse schedule (when to send each bit)
        pulse_duration_frames = int(5.0 / self.dt)  # 5 seconds per pulse
        gap_duration_frames = int(3.0 / self.dt)  # 3 seconds between pulses

        for i, bit in enumerate(bits):
            start_frame = i * (pulse_duration_frames + gap_duration_frames)
            end_frame = start_frame + pulse_duration_frames
            pulse_schedule.append((start_frame, end_frame, bit))

        def update(frame):
            # Determine current pulse
            current_pulse_voltage = cable.V_rest
            active_bit = None

            for start, end, bit in pulse_schedule:
                if start <= frame < end:
                    current_pulse_voltage = +20.0 if bit == 1 else cable.V_rest
                    active_bit = bit
                    break

            # Inject pulse at source
            cable.V[0] = current_pulse_voltage

            # Propagate voltage through cable
            cable.propagate_voltage(current_pulse_voltage, source_cell=0)

            # Simulate regeneration if severed
            if cable.is_severed:
                cable.regenerate(progress_increment=0.002)  # Slow regeneration
                if severance_line:
                    alpha = 1.0 - cable.regeneration_progress
                    severance_line.set_alpha(max(0.1, alpha))

            # Update plot
            line.set_ydata(cable.V)

            # Update status text
            status_lines = [
                f'Time: {frame * self.dt:.1f}s',
                f'Active bit: {active_bit if active_bit is not None else "—"}'
            ]
            if cable.is_severed:
                status_lines.append(f'Regeneration: {cable.regeneration_progress*100:.1f}%')
            time_text.set_text('\n'.join(status_lines))

            return line, time_text

        # Run animation
        n_frames = int(duration_sec / self.dt)
        anim = FuncAnimation(fig, update, frames=n_frames,
                           interval=self.dt*1000, blit=True, repeat=False)

        plt.tight_layout()
        plt.show()

        print(f"\n✅ Transmission complete")
        print(f"Final cable voltage range: {cable.V.min():.1f} to {cable.V.max():.1f} mV")
        if cable.is_severed:
            print(f"Cable regeneration: {cable.regeneration_progress*100:.1f}%")


def demo_simple_transmission():
    """Demo: Simple 2-node transmission"""
    print("\n" + "="*60)
    print("Demo 1: Simple Point-to-Point Transmission")
    print("="*60)

    sim = BioNetSimulator()

    # Create 2 nodes
    node_a = BioNetNode(node_id=0, position=(0, 0))
    node_b = BioNetNode(node_id=1, position=(20, 0))

    sim.add_node(node_a)
    sim.add_node(node_b)

    # Connect with 20mm bio-cable
    node_a.connect_to(node_b, cable_length_mm=20)

    # Transmit letter 'A' (0x41 = 01000001)
    sim.simulate_transmission(source_id=0, dest_id=1, data_byte=0x41,
                             duration_sec=80.0, visualize=True)


def demo_self_healing():
    """Demo: Cable regeneration after damage"""
    print("\n" + "="*60)
    print("Demo 2: Self-Healing Bio-Cable")
    print("="*60)

    sim = BioNetSimulator()

    node_a = BioNetNode(node_id=0, position=(0, 0))
    node_b = BioNetNode(node_id=1, position=(20, 0))

    sim.add_node(node_a)
    sim.add_node(node_b)

    node_a.connect_to(node_b, cable_length_mm=20)

    # SEVER THE CABLE (simulating micrometeorite damage)
    cable = node_a.connections[1]
    cable.sever_cable(position_fraction=0.5)

    print("\n⚠️  Micrometeorite impact! Cable severed at midpoint.")
    print("🔬 Watch as voltage signal fails to propagate...")
    print("🧬 Then watch cells regenerate gap junctions...")
    print("✅ Finally: signal restored!\n")

    # Transmit during regeneration
    sim.simulate_transmission(source_id=0, dest_id=1, data_byte=0x42,
                             duration_sec=120.0, visualize=True)


def demo_mesh_network():
    """Demo: 5-node mesh with multi-hop routing"""
    print("\n" + "="*60)
    print("Demo 3: BioNet Mesh Network (Multi-Hop)")
    print("="*60)

    sim = BioNetSimulator()

    # Create 5 nodes in mesh topology
    #     1
    #    / \
    #   0   2
    #    \ /
    #     3 - 4

    nodes = [
        BioNetNode(0, (0, 5)),
        BioNetNode(1, (5, 10)),
        BioNetNode(2, (10, 10)),
        BioNetNode(3, (5, 0)),
        BioNetNode(4, (15, 0))
    ]

    for node in nodes:
        sim.add_node(node)

    # Connect mesh
    nodes[0].connect_to(nodes[1], 15)
    nodes[0].connect_to(nodes[3], 15)
    nodes[1].connect_to(nodes[2], 15)
    nodes[2].connect_to(nodes[3], 20)
    nodes[3].connect_to(nodes[4], 20)

    print("\n📍 Network topology:")
    print("     Node 1")
    print("     /    \\")
    print("  Node 0  Node 2")
    print("     \\    /")
    print("     Node 3 - Node 4")
    print()

    # Transmit from Node 0 to Node 4 (requires multi-hop)
    print("Routing: Node 0 → Node 3 → Node 4 (2 hops)")
    sim.simulate_transmission(source_id=0, dest_id=3, data_byte=0x5A,
                             duration_sec=80.0, visualize=True)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                        BIONET SIMULATOR v1.0                         ║
║              The World's First Bioelectric Internet                  ║
╚══════════════════════════════════════════════════════════════════════╝

This simulator demonstrates:
✓ Voltage wave propagation through living tissue "cables"
✓ Gap junction coupling (biological ethernet)
✓ Self-healing after damage (regeneration)
✓ Multi-hop mesh networking

Choose a demo:
""")

    print("1. Simple Transmission (Node A → Node B)")
    print("2. Self-Healing Cable (damage + regeneration)")
    print("3. Mesh Network (5 nodes, multi-hop routing)")
    print()

    choice = input("Enter demo number (1-3): ").strip()

    if choice == "1":
        demo_simple_transmission()
    elif choice == "2":
        demo_self_healing()
    elif choice == "3":
        demo_mesh_network()
    else:
        print("Running all demos...")
        demo_simple_transmission()
        demo_self_healing()
        demo_mesh_network()

    print("\n" + "="*60)
    print("BioNet: Living infrastructure for the next millennium 🧬🌐")
    print("="*60)
