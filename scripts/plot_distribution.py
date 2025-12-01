"""
Generate PM2.5 distribution histogram across all cities.

This script creates a histogram showing the overall distribution of PM2.5
values across all cities, with EPA standard threshold markers and summary
statistics.

Run from scripts directory:
    python3 plot_distribution.py
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# Add parent directory to path to import air_quality modules
sys.path.append('..')

from air_quality.data_loader import load_pm25_data
from air_quality.statistics import calculate_daily_mean
from plot_helpers import get_plot_style


def create_distribution_plot(df, output_path='figures/pm25_distribution.pdf'):
    """
    Create histogram showing overall PM2.5 distribution.

    This figure displays the frequency distribution of PM2.5 values across
    all cities combined, with vertical lines marking key EPA thresholds
    and summary statistics.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: date, city, pollutant, value
    output_path : str, default='figures/pm25_distribution.pdf'
        Path to save the output figure

    Returns
    -------
    None
        Saves figure to specified path
    """
    # Apply plot style
    mpl.rcParams.update(get_plot_style())

    # Get all PM2.5 values
    all_values = df['value'].values

    # Calculate summary statistics
    mean_val = calculate_daily_mean(all_values)
    median_val = np.median(all_values)
    std_val = np.std(all_values)
    p95 = np.percentile(all_values, 95)

    # EPA thresholds
    epa_standard = 35.0  # Daily standard
    who_guideline = 15.0  # WHO guideline
    unhealthy_threshold = 55.4  # Unhealthy for Sensitive Groups

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create histogram
    n, bins, patches = ax.hist(
        all_values,
        bins=50,
        color='#1f77b4',
        alpha=0.7,
        edgecolor='black',
        linewidth=0.5
    )

    # Add vertical lines for thresholds
    ax.axvline(
        who_guideline,
        color='#2ca02c',
        linestyle='--',
        linewidth=2,
        label=f'WHO Guideline ({who_guideline} μg/m³)',
        alpha=0.8
    )

    ax.axvline(
        epa_standard,
        color='#ff7f0e',
        linestyle='--',
        linewidth=2,
        label=f'EPA Standard ({epa_standard} μg/m³)',
        alpha=0.8
    )

    ax.axvline(
        unhealthy_threshold,
        color='#d62728',
        linestyle='--',
        linewidth=2,
        label=f'Unhealthy ({unhealthy_threshold} μg/m³)',
        alpha=0.8
    )

    # Add mean line
    ax.axvline(
        mean_val,
        color='black',
        linestyle='-',
        linewidth=2,
        label=f'Mean ({mean_val:.1f} μg/m³)',
        alpha=0.8
    )

    # Create statistics text box
    stats_text = (
        f'Summary Statistics\n'
        f'─────────────────\n'
        f'Mean: {mean_val:.1f} μg/m³\n'
        f'Median: {median_val:.1f} μg/m³\n'
        f'Std Dev: {std_val:.1f} μg/m³\n'
        f'95th Percentile: {p95:.1f} μg/m³\n'
        f'Total Days: {len(all_values):,}'
    )

    # Add text box in upper right
    ax.text(
        0.98, 0.97,
        stats_text,
        transform=ax.transAxes,
        verticalalignment='top',
        horizontalalignment='right',
        fontsize=10,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, pad=0.8),
        family='monospace'
    )

    # Labels and title
    ax.set_xlabel('PM2.5 Concentration (μg/m³)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency (Number of Days)', fontsize=12, fontweight='bold')
    ax.set_title(
        'PM2.5 Distribution Across All Cities - 2024',
        fontsize=14,
        fontweight='bold',
        pad=15
    )

    # Grid and legend
    ax.grid(axis='y', alpha=0.3, linestyle=':')
    ax.legend(loc='upper right', fontsize=10, bbox_to_anchor=(0.98, 0.55))

    # Set x-axis limits for better visualization
    ax.set_xlim(0, max(all_values.max(), unhealthy_threshold + 10))

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to {output_path}")
    plt.close()


def main():
    """Main execution function."""
    # Data path (run from scripts directory)
    data_path = Path('../data/all_cities_pm25.csv')

    # Check if data file exists
    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        print("Please run fetch_data.py first to download the data.")
        return

    # Load data
    print(f"Loading data from {data_path}...")
    df = load_pm25_data(str(data_path))
    print(f"Loaded {len(df)} records for {len(df['city'].unique())} cities")

    # Create output directory if needed
    output_dir = Path('../figures')
    output_dir.mkdir(exist_ok=True)

    # Generate figure
    output_path = output_dir / 'pm25_distribution.pdf'
    print("\nGenerating PM2.5 distribution histogram...")
    create_distribution_plot(df, str(output_path))

    print("\nDone!")


if __name__ == '__main__':
    main()

