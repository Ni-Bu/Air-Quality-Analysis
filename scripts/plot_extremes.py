"""
Generate extreme events comparison bar chart for PM2.5 data.

This script creates a grouped bar chart comparing exceedance counts across
cities using multiple threshold definitions (EPA standard and 95th percentile).

Run from scripts directory:
    python3 plot_extremes.py
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# Add parent directory to path to import air_quality modules
sys.path.append('..')

from air_quality.data_loader import (
    load_pm25_data, get_cities_list, filter_by_city
)
from air_quality.statistics import calculate_exceedance_count
from air_quality.extremes import identify_extremes_threshold
from plot_helpers import get_plot_style, get_city_colors


def create_extremes_comparison(
    df,
    output_path='figures/extreme_events.pdf'
):
    """
    Create grouped bar chart comparing extreme event counts across cities.

    Compares exceedance counts using two different thresholds:
    1. EPA 24-hour standard (35 μg/m³)
    2. Dataset 95th percentile (adaptive threshold)

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: date, city, pollutant, value
    output_path : str, default='figures/extreme_events.pdf'
        Path to save the output figure

    Returns
    -------
    None
        Saves figure to specified path
    """
    # Apply plot style
    mpl.rcParams.update(get_plot_style())

    # Get cities and colors
    cities = get_cities_list(df)
    colors = get_city_colors()

    # Define thresholds
    epa_standard = 35.0  # EPA 24-hour standard
    # Calculate 95th percentile across all data
    percentile_95 = np.percentile(df['value'].dropna(), 95)

    # Calculate exceedance counts for each city and threshold
    epa_counts = []
    percentile_counts = []

    for city in cities:
        city_df = filter_by_city(df, city)
        values = city_df['value'].values

        # Count EPA standard exceedances
        epa_count = calculate_exceedance_count(values, epa_standard)
        epa_counts.append(epa_count)

        # Count 95th percentile exceedances
        p95_count = calculate_exceedance_count(values, percentile_95)
        percentile_counts.append(p95_count)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))

    # Set up grouped bar positions
    x = np.arange(len(cities))
    width = 0.35  # Width of bars

    # Create grouped bars
    bars1 = ax.bar(
        x - width/2,
        epa_counts,
        width,
        label=f'EPA Standard (>{epa_standard:.0f} μg/m³)',
        color='#FF6B6B',
        alpha=0.8,
        edgecolor='black',
        linewidth=1.2
    )

    bars2 = ax.bar(
        x + width/2,
        percentile_counts,
        width,
        label=f'95th Percentile (>{percentile_95:.1f} μg/m³)',
        color='#4ECDC4',
        alpha=0.8,
        edgecolor='black',
        linewidth=1.2
    )

    # Add value labels on bars
    def add_value_labels(bars):
        """Add text labels on top of bars."""
        for bar in bars:
            height = bar.get_height()
            if height > 0:  # Only label non-zero bars
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height,
                    f'{int(height)}',
                    ha='center',
                    va='bottom',
                    fontsize=10,
                    fontweight='bold'
                )

    add_value_labels(bars1)
    add_value_labels(bars2)

    # Styling
    ax.set_xlabel('City', fontsize=13, fontweight='bold')
    ax.set_ylabel('Number of Exceedance Days', fontsize=13, fontweight='bold')
    ax.set_title(
        'PM2.5 Exceedance Events by City - 2024\n'
        'Comparison of EPA Standard vs. 95th Percentile Thresholds',
        fontsize=15,
        fontweight='bold',
        pad=20
    )
    ax.set_xticks(x)
    ax.set_xticklabels(cities, rotation=45, ha='right')
    ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
    ax.grid(axis='y', alpha=0.3, linestyle=':')

    # Set y-axis to start at 0
    ax.set_ylim(bottom=0)

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    # Also save as PNG for easier viewing
    png_path = output_path.replace('.pdf', '.png')
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    
    print(f"Figure saved to {output_path}")
    print(f"Figure saved to {png_path}")
    plt.close()

    # Print summary statistics
    print("\n=== Exceedance Summary ===")
    print(f"EPA Standard (>{epa_standard:.0f} μg/m³):")
    for city, count in zip(cities, epa_counts):
        print(f"  {city}: {count} days")
    print(f"\n95th Percentile (>{percentile_95:.1f} μg/m³):")
    for city, count in zip(cities, percentile_counts):
        print(f"  {city}: {count} days")


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
    output_path = output_dir / 'extreme_events.pdf'
    print("\nGenerating extreme events comparison chart...")
    create_extremes_comparison(df, str(output_path))

    print("\nDone!")


if __name__ == '__main__':
    main()

