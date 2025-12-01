"""
Create time series visualization of PM2.5 data across US cities.

This script generates a line plot comparing PM2.5 levels across six US cities
in 2024, with EPA air quality standard reference line.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates

from air_quality.plotting import get_plot_style, get_city_colors


CITIES = [
    'Los Angeles', 'Fresno', 'Phoenix',
    'Denver', 'Salt Lake City', 'Pittsburgh'
]

def load_data():
    """
    Load PM2.5 data from CSV file.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: date, city, pollutant, value
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(
        script_dir, '..', 'data', 'all_cities_pm25.csv'
    )
    pm25_data = pd.read_csv(data_file)
    pm25_data['date'] = pd.to_datetime(pm25_data['date'])
    return pm25_data

def create_plot(pm25_data, output_file=None):
    """
    Create time series comparison plot of PM2.5 across cities.

    Parameters
    ----------
    pm25_data : pd.DataFrame
        DataFrame containing PM2.5 data with date, city, and value columns
    output_file : str, optional
        Output file path. Defaults to figures/air_quality_timeseries.pdf

    Returns
    -------
    None
        Saves figure to file
    """
    # Apply plot style
    mpl.rcParams.update(get_plot_style())
    
    # Get city colors
    city_colors = get_city_colors()
    
    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot each city's data
    for city in CITIES:
        city_data = pm25_data[pm25_data['city'] == city]
        if not city_data.empty:
            ax.plot(
                city_data['date'],
                city_data['value'],
                alpha=0.8,
                label=city,
                color=city_colors.get(city, 'gray')
            )

    # Add EPA standard reference line
    ax.axhline(
        y=35,
        color='red',
        linestyle='--',
        linewidth=2,
        label='EPA Standard (35 µg/m³)',
        alpha=0.8
    )

    # Labels and title
    ax.set_ylabel('PM2.5 (µg/m³)', fontweight='bold')
    ax.set_xlabel('Date (2024)', fontweight='bold')
    ax.set_title(
        'Air Quality Comparison Across US Cities (2024)',
        fontweight='bold'
    )

    # Position legend outside plot area for clarity
    ax.legend(
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        ncol=1,
        borderaxespad=0
    )

    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0, top=85)
    ax.set_xlim(pd.Timestamp('2024-01-01'), pd.Timestamp('2024-12-31'))

    # Format date axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    plt.tight_layout()

    # Save as PDF for vector graphics quality
    if output_file is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(
            script_dir, '..', 'figures', 'air_quality_timeseries.pdf'
        )

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300)
    print(f"Figure saved to: {output_file}")

def main():
    """Main execution function."""
    print("Loading data...")
    pm25_data = load_data()

    print("Creating plot...")
    create_plot(pm25_data)

    print("Done!")


if __name__ == "__main__":
    main()