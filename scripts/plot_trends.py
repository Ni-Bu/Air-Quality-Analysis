"""
Generate trend analysis scatter plots with fitted linear trends.

This script creates a 2x3 grid of scatter plots showing daily PM2.5 values
over time with fitted linear trend lines, R-squared values, and slope
annotations for each city.

Run from scripts directory:
    python3 plot_trends.py
"""

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# Add parent directory to path to import air_quality modules
sys.path.append('..')

from air_quality.data_loader import (  # noqa: E402
    load_pm25_data, get_cities_list, filter_by_city
)
from air_quality.trends import calculate_linear_trend  # noqa: E402
from plot_helpers import (  # noqa: E402
    get_plot_style, setup_subplot_grid, get_city_colors
)


def create_trend_analysis(
    df,
    output_path='../figures/trend_analysis.pdf'
):
    """
    Create scatter plots with fitted trend lines for all cities.

    Shows daily PM2.5 values as scatter points with linear regression
    trend lines. Annotates each subplot with R-squared and slope values
    to quantify trend strength and direction.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: date, city, pollutant, value
    output_path : str, default='../figures/trend_analysis.pdf'
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

    # Find global max for consistent y-axis scaling
    global_max = df['value'].max()
    # Round up to nearest 10 for cleaner axis
    y_max = np.ceil(global_max / 10) * 10

    # Create 2x3 subplot grid
    fig, axes = setup_subplot_grid(nrows=2, ncols=3, figsize=(15, 10))
    axes = axes.flatten()

    # Create scatter plot with trend line for each city
    for idx, city in enumerate(cities):
        ax = axes[idx]

        # Filter data for this city
        city_df = filter_by_city(df, city)
        city_df = city_df.sort_values('date')

        dates = city_df['date']
        values = city_df['value'].values

        # Calculate linear trend
        slope, intercept, r_squared, p_value = calculate_linear_trend(
            dates, values
        )

        # Convert dates to ordinal for plotting trend line
        dates_ordinal = dates.map(pd.Timestamp.toordinal).values
        trend_line = slope * dates_ordinal + intercept

        # Scatter plot of actual data
        ax.scatter(
            dates,
            values,
            color=colors[city],
            alpha=0.5,
            s=20,
            label='Daily PM2.5',
            edgecolors='none'
        )

        # Plot trend line
        ax.plot(
            dates,
            trend_line,
            color=colors[city],
            linewidth=2.5,
            linestyle='--',
            label='Linear Trend',
            alpha=0.9
        )

        # Add EPA standard reference line
        ax.axhline(
            y=35.0,
            color='red',
            linestyle=':',
            linewidth=1.5,
            alpha=0.7,
            label='EPA Standard'
        )

        # Format title and labels
        ax.set_title(f'{city}', fontweight='bold', fontsize=13)
        ax.set_xlabel('Date', fontsize=11)
        ax.set_ylabel('PM2.5 (μg/m³)', fontsize=11)

        # Set consistent y-axis limits across all subplots
        ax.set_ylim(0, y_max)

        # Format x-axis dates
        ax.tick_params(axis='x', rotation=45)
        fig.autofmt_xdate()

        # Add text box with statistics
        # Slope is per day, convert to per year for readability
        slope_per_year = slope * 365.25

        # Format p-value for display
        if p_value < 0.001:
            p_text = 'p < 0.001'
        elif p_value < 0.01:
            p_text = 'p < 0.01'
        elif p_value < 0.05:
            p_text = 'p < 0.05'
        else:
            p_text = f'p = {p_value:.3f}'

        # Create annotation text
        stats_text = (
            f'R² = {r_squared:.3f}\n'
            f'Slope = {slope_per_year:.2f} μg/m³/year\n'
            f'{p_text}'
        )

        # Add text box in upper right corner
        ax.text(
            0.98, 0.98,
            stats_text,
            transform=ax.transAxes,
            verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(
                boxstyle='round',
                facecolor='white',
                alpha=0.8,
                edgecolor='gray'
            ),
            fontsize=9
        )

        # Add legend only to first subplot
        if idx == 0:
            ax.legend(loc='upper left', fontsize=9, framealpha=0.9)

        # Add grid for readability
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)

    # Overall title
    fig.suptitle(
        'PM2.5 Trend Analysis: Daily Values with Linear Fits (2024)',
        fontsize=16,
        fontweight='bold',
        y=0.995
    )

    # Adjust layout to prevent overlap
    plt.tight_layout(rect=[0, 0, 1, 0.99])

    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f'Saved trend analysis figure to: {output_path}')
    plt.close()


def main():
    """Main function to load data and generate trend analysis figure."""
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
    print('Generating trend analysis figure...')
    create_trend_analysis(df)

    print('Done!')


if __name__ == '__main__':
    main()
