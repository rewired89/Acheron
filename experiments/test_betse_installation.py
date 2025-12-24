"""
BETSE Integration Test
======================

Test that BETSE is installed correctly and explore its capabilities
for planarian bioelectric simulations.

BETSE (BioElectric Tissue Simulation Engine) is the gold standard for
bioelectric tissue modeling from the Levin Lab.
"""

import sys

def test_betse_installation():
    """
    Verify BETSE is installed and importable.
    """
    print("\n" + "="*70)
    print("BETSE INSTALLATION CHECK")
    print("="*70 + "\n")

    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print()

    try:
        import betse
        print(f"✓ BETSE installed successfully")
        print(f"  Version: {betse.__version__ if hasattr(betse, '__version__') else 'Unknown'}")
        print(f"  Location: {betse.__file__}")
        print()

        # Try importing key modules
        modules_to_test = [
            'betse.science.config.model.modelconfig',
            'betse.science.tissue',
            'betse.science.phase',
            'betse.util.io.log',
        ]

        print("Testing BETSE modules:")
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                print(f"  ✓ {module_name}")
            except ImportError as e:
                print(f"  ✗ {module_name}: {e}")

        return True

    except ImportError as e:
        print(f"✗ BETSE not found: {e}")
        print()
        print("Install BETSE with: pip install betse")
        return False


def test_betsee_installation():
    """
    Verify BETSEE (GUI) is installed.
    """
    print("\n" + "="*70)
    print("BETSEE INSTALLATION CHECK")
    print("="*70 + "\n")

    try:
        import betsee
        print(f"✓ BETSEE installed successfully")
        print(f"  Version: {betsee.__version__ if hasattr(betsee, '__version__') else 'Unknown'}")
        print(f"  Location: {betsee.__file__}")
        print()
        print("Note: BETSEE is the GUI interface for BETSE")
        print("Run 'betsee' from command line to launch GUI")
        return True

    except ImportError as e:
        print(f"✗ BETSEE not found: {e}")
        print()
        print("BETSEE is optional (GUI only)")
        print("Install with: pip install betsee")
        return False


def explore_betse_capabilities():
    """
    Explore what BETSE can do for our planarian simulations.
    """
    print("\n" + "="*70)
    print("BETSE CAPABILITIES FOR ACHERON")
    print("="*70 + "\n")

    capabilities = {
        "Cell Networks": [
            "2D/3D tissue grids",
            "Gap junction coupling",
            "Ion channel dynamics",
            "Membrane potential computation"
        ],
        "Ion Dynamics": [
            "Na+, K+, Cl-, Ca2+ diffusion",
            "Voltage-gated channels",
            "Ligand-gated channels",
            "Pump dynamics (Na+/K+ ATPase)"
        ],
        "Bioelectric Phenomena": [
            "Resting potential gradients",
            "Tissue-wide field potentials",
            "Endogenous currents",
            "Pattern formation"
        ],
        "Acheron Use Cases": [
            "Validate our persistence simulator",
            "Test realistic ion channel parameters",
            "Model optogenetic perturbations",
            "Compare to published planarian data"
        ]
    }

    for category, items in capabilities.items():
        print(f"{category}:")
        for item in items:
            print(f"  • {item}")
        print()

    print("="*70)
    print("NEXT STEPS")
    print("="*70 + "\n")
    print("1. Run our simplified simulator first (bioelectric_persistence.py)")
    print("2. Compare results to BETSE for validation")
    print("3. Use BETSE for parameter fitting (realistic ion channel values)")
    print("4. Export BETSE results for investor demos")
    print()


def create_betse_comparison_plan():
    """
    Plan for validating our simulator against BETSE.
    """
    print("\n" + "="*70)
    print("VALIDATION STRATEGY: Acheron vs BETSE")
    print("="*70 + "\n")

    plan = """
Our Strategy: Two-Tier Simulation Approach

TIER 1: Acheron Simplified Simulator (FAST)
├─ Purpose: Rapid prototyping, investor demos
├─ Speed: Seconds to minutes
├─ Accuracy: Qualitative (proves concept)
└─ Use for: Pattern persistence proofs, parameter sweeps

TIER 2: BETSE Full Simulation (ACCURATE)
├─ Purpose: Scientific validation, publications
├─ Speed: Minutes to hours
├─ Accuracy: Quantitative (publishable)
└─ Use for: Grant applications, lab partnerships

Validation Protocol:
1. Run simple case in both simulators (single bit, 24hr)
2. Compare: voltage ranges, persistence times, diffusion rates
3. Adjust Acheron parameters to match BETSE
4. Publish: "Acheron results validated against BETSE"

Why This Matters for Patents:
- Shows due diligence (used gold-standard tool)
- Strengthens claims (backed by Levin Lab's simulator)
- Demonstrates feasibility (not just theoretical)
"""

    print(plan)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("ACHERON - BETSE INTEGRATION CHECK")
    print("="*70)

    betse_ok = test_betse_installation()
    betsee_ok = test_betsee_installation()

    if betse_ok:
        explore_betse_capabilities()
        create_betse_comparison_plan()
    else:
        print("\n⚠️  BETSE not found. Install it first:")
        print("    pip install betse")
        print()
        print("Our simplified simulator will still work!")
        print("BETSE is for validation and scientific rigor.")

    print("\n" + "="*70)
    print("RECOMMENDATION")
    print("="*70 + "\n")

    if betse_ok:
        print("✓ BETSE is ready!")
        print()
        print("Next steps:")
        print("1. Run: python simulations/bioelectric_persistence.py")
        print("2. Then: python experiments/betse_integration.py (we'll create this)")
        print("3. Compare results for validation")
    else:
        print("Start with our simplified simulator:")
        print("  python simulations/bioelectric_persistence.py")
        print()
        print("Install BETSE later for validation:")
        print("  pip install betse")

    print()
