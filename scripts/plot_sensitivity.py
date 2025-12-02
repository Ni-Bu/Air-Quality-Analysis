"""
Generate sensitivity analysis plot showing robustness to threshold choice.

This script creates a multi-line plot showing how the count of extreme days
varies with different threshold definitions, demonstrating the robustness
of findings to threshold choice.

Run from scripts directory:
    python3 plot_sensitivity.py
"""

from pathlib import Path
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# Add parent directory to path to import air_quality modules
sys.path.append('..')

from air_quality.data_loader import (  # noqa: E402
    load_pm25_data, get_cities_list, filter_by_city
)
from air_quality.extremes import identify_extremes_threshold  # noqa: E402
from plot_helpers import (  # noqa: E402
    get_plot_style, get_city_colors
)


def create_sensitivity_analysis(
    df,
    output_path='../figures/sensitivity_analysis.pdf'
):
    """
    Create sensitivity analysis plot for extreme event definitions.

    Shows how the count of extreme days varies with threshold values,
    demonstrating robustness of findings to threshold choice. Tests
    thresholds from WHO guideline (15 μg/m³) to EPA standard (40 μg/m³).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: date, city, pollutant, value
    output_path : str, default='../figures/sensitivity_analysis.pdf'
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

    # Define threshold range: WHO guideline (15) to above EPA standard (40)
    thresholds = np.arange(15, 41, 1)  # 15 to 40 μg/m³ in 1 μg/m³ steps

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    # Calculate and plot exceedance counts for each city
    for city in cities:
        # Filter data for this city
        city_df = filter_by_city(df, city)

        # Rename columns to match extremes module expectations
        city_df_renamed = city_df.rename(
            columns={'date': 'Date', 'value': 'PM2.5'}
        )

        # Count exceedances for each threshold
        exceedance_counts = []
        for threshold in thresholds:
            extremes = identify_extremes_threshold(
                city_df_renamed,
                threshold
            )
            exceedance_counts.append(len(extremes))

        # Plot line for this city
        ax.plot(
            thresholds,
            exceedance_counts,
            color=colors[city],
            linewidth=2.5,
            marker='o',
            markersize=4,
            label=city,
            alpha=0.85
        )

    # Add reference lines for key thresholds
    # WHO guideline (15 μg/m³)
    ax.axvline(
        x=15,
        color='green',
        linestyle=':',
        linewidth=2,
        alpha=0.6,
        label='WHO Guideline'
    )

    # EPA standard (35 μg/m³)
    ax.axvline(
        x=35,
        color='red',
        linestyle=':',
        linewidth=2,
        alpha=0.6,
        label='EPA Standard'
    )

    # Labels and title
    ax.set_xlabel('PM2.5 Threshold (μg/m³)', fontsize=13, fontweight='bold')
    ax.set_ylabel(
        'Number of Days Exceeding Threshold',
        fontsize=13,
        fontweight='bold'
    )
    ax.set_title(
        'Sensitivity Analysis: Extreme Event Counts vs. Threshold Definition',
        fontsize=15,
        fontweight='bold',
        pad=20
    )

    # Add legend outside plot area to avoid line overlap
    ax.legend(
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        fontsize=11,
        framealpha=0.95,
        ncol=1
    )

    # Add grid for readability
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    # Set x-axis limits with some padding
    ax.set_xlim(14, 41)

    # Ensure y-axis starts at 0
    ax.set_ylim(bottom=0)

    # Add text box with interpretation
    interpretation_text = (
        'Lower thresholds (e.g., WHO guideline)\n'
        'identify more exceedance days.\n'
        'EPA standard shows fewer exceedances.'
    )
    ax.text(
        0.02, 0.98,
        interpretation_text,
        transform=ax.transAxes,
        verticalalignment='top',
        horizontalalignment='left',
        bbox=dict(
            boxstyle='round',
            facecolor='white',
            alpha=0.9,
            edgecolor='gray'
        ),
        fontsize=10
    )

    # Adjust layout
    plt.tight_layout()

    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f'Saved sensitivity analysis figure to: {output_path}')
    plt.close()


def main():
    """Main function to load data and generate sensitivity analysis figure."""
    # Load data
    data_path = Path('../data/all_cities_pm25.csv')

    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        print("Please run fetch_data.py first to download the data.")
        sys.exit(1)

    print(f'Loading data from {data_path}...')
    df = load_pm25_data(data_path)

    print(f'Data loaded: {len(df)} records for {len(df["city"].unique())} '
          f'cities')

    # Generate figure
    print('Generating sensitivity analysis figure...')
    create_sensitivity_analysis(df)

    print('Done!')


if __name__ == '__main__':
    main()
