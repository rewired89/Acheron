"""
Competitive Landscape Visualization
====================================

Generate charts comparing Acheron to competitors on key metrics.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)


def plot_lifespan_comparison():
    """
    Compare device lifespan across competitors.
    """
    companies = ['Cortical Labs\n(CL-1)', 'Koniku\n(Konikore)', 'FinalSpark\n(Organoids)', 'Acheron\n(Planarians)']
    lifespans = [6, 24, 12, 1000]  # months (Acheron shown as effectively infinite)
    colors = ['#FF6B6B', '#FFA500', '#4ECDC4', '#45B7D1']

    fig, ax = plt.subplots()

    bars = ax.barh(companies, lifespans, color=colors, edgecolor='black', linewidth=1.5)

    # Annotate bars
    for bar, lifespan in zip(bars, lifespans):
        width = bar.get_width()
        if lifespan < 100:
            label = f'{lifespan} months'
        else:
            label = 'Indefinite\n(regenerates)'

        ax.text(width + 20, bar.get_y() + bar.get_height()/2,
               label, ha='left', va='center', fontsize=11, fontweight='bold')

    ax.set_xlabel('Lifespan (months)', fontsize=12, fontweight='bold')
    ax.set_title('Biocomputing Device Lifespan Comparison', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 200)  # Cap display for readability

    # Add reference line at 24 months (2 years)
    ax.axvline(x=24, color='red', linestyle='--', linewidth=2, alpha=0.5, label='2-year mark')
    ax.legend()

    plt.tight_layout()
    plt.savefig('analysis/lifespan_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: analysis/lifespan_comparison.png")


def plot_feature_matrix():
    """
    Create a feature comparison matrix (heatmap style).
    """
    companies = ['Cortical Labs', 'Koniku', 'FinalSpark', 'Acheron']
    features = [
        'Persistent\nMemory',
        'Self-Healing',
        'Radiation\nResistant',
        'Low Energy',
        'Commercially\nAvailable',
        'General\nComputing'
    ]

    # 0 = No, 0.5 = Partial, 1 = Yes
    data = np.array([
        [0, 0, 0, 0.5, 1, 1],      # Cortical Labs
        [0, 0, 0, 0.5, 1, 0],      # Koniku
        [0, 0, 0, 1, 0.5, 0.5],    # FinalSpark
        [1, 1, 1, 1, 0, 1]         # Acheron
    ])

    fig, ax = plt.subplots(figsize=(12, 8))

    # Create heatmap
    im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)

    # Set ticks
    ax.set_xticks(np.arange(len(features)))
    ax.set_yticks(np.arange(len(companies)))
    ax.set_xticklabels(features, fontsize=11)
    ax.set_yticklabels(companies, fontsize=12, fontweight='bold')

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")

    # Add text annotations
    for i in range(len(companies)):
        for j in range(len(features)):
            value = data[i, j]
            if value == 1:
                text = '✓'
                color = 'darkgreen'
            elif value == 0.5:
                text = '~'
                color = 'orange'
            else:
                text = '✗'
                color = 'darkred'

            ax.text(j, i, text, ha="center", va="center",
                   color=color, fontsize=20, fontweight='bold')

    ax.set_title('Biocomputing Platform Feature Comparison', fontsize=16, fontweight='bold', pad=20)

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Capability Level', rotation=270, labelpad=20, fontsize=11)
    cbar.set_ticks([0, 0.5, 1])
    cbar.set_ticklabels(['No', 'Partial', 'Yes'])

    plt.tight_layout()
    plt.savefig('analysis/feature_matrix.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: analysis/feature_matrix.png")


def plot_cost_of_ownership():
    """
    Total cost of ownership over 5 years.
    """
    years = np.arange(0, 6)  # 0 to 5 years

    # Cortical Labs: $35K every 6 months
    cortical_costs = 35000 * (years * 2 + 1)  # +1 for initial purchase

    # Koniku: $50K initial (estimated), $20K every 2 years
    koniku_costs = 50000 + 20000 * (years // 2)

    # Acheron: $50K initial (64-bit), no replacement
    acheron_costs = np.ones_like(years) * 50000

    fig, ax = plt.subplots()

    ax.plot(years, cortical_costs / 1000, 'o-', linewidth=2.5, label='Cortical Labs (CL-1)', color='#FF6B6B', markersize=8)
    ax.plot(years, koniku_costs / 1000, 's-', linewidth=2.5, label='Koniku', color='#FFA500', markersize=8)
    ax.plot(years, acheron_costs / 1000, '^-', linewidth=2.5, label='Acheron (64-bit)', color='#45B7D1', markersize=8)

    ax.set_xlabel('Years of Operation', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Cost of Ownership ($K)', fontsize=12, fontweight='bold')
    ax.set_title('5-Year Total Cost of Ownership Comparison', fontsize=16, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)

    # Annotate final costs
    ax.text(5, cortical_costs[-1] / 1000 + 20, f'${cortical_costs[-1]/1000:.0f}K',
           fontsize=10, fontweight='bold', color='#FF6B6B')
    ax.text(5, koniku_costs[-1] / 1000 + 20, f'${koniku_costs[-1]/1000:.0f}K',
           fontsize=10, fontweight='bold', color='#FFA500')
    ax.text(5, acheron_costs[-1] / 1000 - 20, f'${acheron_costs[-1]/1000:.0f}K (flat)',
           fontsize=10, fontweight='bold', color='#45B7D1')

    plt.tight_layout()
    plt.savefig('analysis/cost_of_ownership.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: analysis/cost_of_ownership.png")


def plot_market_positioning():
    """
    2D plot: Lifespan vs. Capabilities
    """
    companies = ['Cortical Labs', 'Koniku', 'FinalSpark', 'Acheron']
    lifespan = [6, 24, 12, 120]  # months (Acheron capped for visualization)
    capabilities = [8, 5, 6, 9]  # Subjective score out of 10
    colors = ['#FF6B6B', '#FFA500', '#4ECDC4', '#45B7D1']
    sizes = [300, 250, 200, 400]

    fig, ax = plt.subplots(figsize=(12, 8))

    for company, x, y, color, size in zip(companies, lifespan, capabilities, colors, sizes):
        ax.scatter(x, y, s=size, c=color, alpha=0.6, edgecolors='black', linewidth=2)
        ax.annotate(company, (x, y), fontsize=11, fontweight='bold',
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.3))

    ax.set_xlabel('Device Lifespan (months)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Technical Capabilities Score (0-10)', fontsize=12, fontweight='bold')
    ax.set_title('Biocomputing Market Positioning:\nLifespan vs. Capabilities', fontsize=16, fontweight='bold')

    # Add quadrant lines
    ax.axhline(y=7, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    ax.axvline(x=24, color='gray', linestyle='--', alpha=0.3, linewidth=1)

    # Annotate quadrants
    ax.text(5, 9.5, 'High Capability\nShort Life', fontsize=10, alpha=0.5, ha='center')
    ax.text(100, 9.5, 'IDEAL ZONE\n(Acheron)', fontsize=11, alpha=0.7, ha='center', fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
    ax.text(5, 5, 'Low Capability\nShort Life', fontsize=10, alpha=0.5, ha='center')
    ax.text(100, 5, 'Long Life\nLow Capability', fontsize=10, alpha=0.5, ha='center')

    ax.set_xlim(0, 130)
    ax.set_ylim(4, 10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('analysis/market_positioning.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: analysis/market_positioning.png")


def generate_all_visualizations():
    """
    Generate all competitive analysis charts.
    """
    print("\n" + "="*60)
    print("GENERATING COMPETITIVE LANDSCAPE VISUALIZATIONS")
    print("="*60 + "\n")

    plot_lifespan_comparison()
    plot_feature_matrix()
    plot_cost_of_ownership()
    plot_market_positioning()

    print("\n" + "="*60)
    print("ALL VISUALIZATIONS COMPLETE")
    print("="*60)
    print("\nGenerated files:")
    print("  - analysis/lifespan_comparison.png")
    print("  - analysis/feature_matrix.png")
    print("  - analysis/cost_of_ownership.png")
    print("  - analysis/market_positioning.png")
    print("\nUse these in investor presentations and grant applications.")
    print("="*60 + "\n")


if __name__ == '__main__':
    generate_all_visualizations()
    plt.show()
