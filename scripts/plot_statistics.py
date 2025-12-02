"""
Generate statistical summary box plots for PM2.5 data across cities.

This script creates a 2x3 grid of box plots showing the distribution of
PM2.5 values for each city, with EPA standard reference lines.

Run from scripts directory:
    python3 plot_statistics.py
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
from plot_helpers import (
    get_plot_style, setup_subplot_grid, get_city_colors
)


def create_statistical_summary(
    df,
    output_path='figures/statistical_summary.pdf'
):
    """
    Create box plot grid showing PM2.5 distributions for all cities.

    Box plots visualize the distribution of PM2.5 values including
    quartiles, median, and outliers. EPA standard reference line
    is added for context.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: date, city, pollutant, value
    output_path : str, default='figures/statistical_summary.pdf'
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

    # EPA standard threshold
    epa_standard = 35.0

    # Find global max for consistent y-axis scaling
    global_max = df['value'].max()
    # Round up to nearest 10 for cleaner axis
    y_max = np.ceil(global_max / 10) * 10

    # Create 2x3 subplot grid
    fig, axes = setup_subplot_grid(nrows=2, ncols=3, figsize=(15, 10))
    axes = axes.flatten()

    # Create box plot for each city
    for idx, city in enumerate(cities):
        ax = axes[idx]

        # Filter data for this city
        city_df = filter_by_city(df, city)
        values = city_df['value'].values

        # Create box plot with matplotlib styling
        ax.boxplot(
            [values],
            widths=0.6,
            patch_artist=True,
            showfliers=True,
            flierprops=dict(
                marker='o',
                markersize=6,
                markerfacecolor='none',
                markeredgecolor='black',
                markeredgewidth=1.0
            ),
            medianprops=dict(color='black', linewidth=2),
            boxprops=dict(
                facecolor=colors[city],
                alpha=0.7,
                edgecolor='black',
                linewidth=1.0
            ),
            whiskerprops=dict(linewidth=1.0, color='black'),
            capprops=dict(linewidth=1.0, color='black')
        )

        # Add EPA standard line
        ax.axhline(
            epa_standard,
            color='red',
            linestyle='--',
            linewidth=2,
            label='EPA Standard (35 μg/m³)',
            alpha=0.8
        )

        # Calculate summary statistics for annotation
        median_val = np.median(values)
        q75 = np.percentile(values, 75)
        max_val = np.max(values)

        # Add text annotation with key statistics
        stats_text = (
            f'Median: {median_val:.1f}\n'
            f'75th %ile: {q75:.1f}\n'
            f'Max: {max_val:.1f}'
        )
        ax.text(
            0.98, 0.97,
            stats_text,
            transform=ax.transAxes,
            verticalalignment='top',
            horizontalalignment='right',
            fontsize=10,
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )

        # Styling
        ax.set_title(city, fontsize=14, fontweight='bold')
        ax.set_ylabel('PM2.5 (μg/m³)', fontsize=12)
        ax.set_xticks([])
        ax.grid(axis='y', alpha=0.3, linestyle=':')
        # Set consistent y-axis limits across all subplots
        ax.set_ylim(0, y_max)

    # Overall title
    fig.suptitle(
        'PM2.5 Distribution by City - 2024',
        fontsize=16,
        fontweight='bold',
        y=0.995
    )
    
    # Create a single legend entry for EPA standard line
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], color='red', linestyle='--', 
                              linewidth=2, label='EPA Standard (35 μg/m³)')]
    fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.95), 
               fontsize=10, framealpha=0.9)

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
    output_path = output_dir / 'statistical_summary.pdf'
    print("\nGenerating statistical summary box plots...")
    create_statistical_summary(df, str(output_path))

    print("\nDone!")


if __name__ == '__main__':
    main()
