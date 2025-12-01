#!/usr/bin/env python3
"""
Enhanced time series visualization of PM2.5 data with rolling averages,
EPA thresholds, and AQI color zones.

This script creates a detailed time series plot showing:
- Raw PM2.5 measurements for each city
- 7-day rolling averages
- EPA standard (35 µg/m³) and unhealthy threshold (55.4 µg/m³)
- Shaded regions between thresholds
- AQI color zones in background

Run from project root:
    PYTHONPATH=. python3 scripts/plot_timeseries.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

from air_quality.plotting import (
    get_plot_style,
    get_city_colors,
    setup_subplot_grid
)
from air_quality.statistics import calculate_rolling_average


def load_data(filepath):
    """Load PM2.5 data from CSV file."""
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    return df


def add_aqi_background(ax):
    """Add AQI color zones as background shading."""
    # EPA PM2.5 AQI breakpoints with colors
    aqi_zones = [
        (0, 12.0, '#00E400', 'Good'),
        (12.0, 35.4, '#FFFF00', 'Moderate'),
        (35.4, 55.4, '#FF7E00', 'Unhealthy for Sensitive'),
        (55.4, 150.4, '#FF0000', 'Unhealthy'),
        (150.4, 250.4, '#8F3F97', 'Very Unhealthy'),
    ]
    
    for y_low, y_high, color, label in aqi_zones:
        ax.axhspan(y_low, y_high, alpha=0.1, color=color, zorder=0)


def plot_enhanced_timeseries(df, output_path):
    """
    Create enhanced time series plot with rolling averages and thresholds.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with columns: date, city, value
    output_path : str
        Path to save the figure (PDF format)
    """
    # Apply plot style
    mpl.rcParams.update(get_plot_style())
    
    # Get city colors
    city_colors = get_city_colors()
    cities = sorted(df['city'].unique())
    
    # Create figure
    fig, ax = setup_subplot_grid(figsize=(14, 8))
    
    # Add AQI background zones
    add_aqi_background(ax)
    
    # Plot each city
    for city in cities:
        city_data = df[df['city'] == city].sort_values('date')
        dates = city_data['date'].values
        values = city_data['value'].values
        
        # Plot raw data with lower alpha
        ax.plot(dates, values, 
                color=city_colors[city],
                alpha=0.3,
                linewidth=1,
                label=f'{city} (daily)')
        
        # Calculate and plot 7-day rolling average
        rolling_avg = calculate_rolling_average(values, window=7)
        
        # Only plot rolling average where it's not NaN
        valid_mask = ~np.isnan(rolling_avg)
        ax.plot(dates[valid_mask], rolling_avg[valid_mask],
                color=city_colors[city],
                linewidth=2.5,
                alpha=0.9,
                label=f'{city} (7-day avg)')
    
    # Add EPA standard line (35 µg/m³)
    ax.axhline(y=35, color='black', linestyle='--', 
               linewidth=2, alpha=0.7,
               label='EPA Standard (35 µg/m³)')
    
    # Add unhealthy threshold line (55.4 µg/m³)
    ax.axhline(y=55.4, color='darkred', linestyle='--',
               linewidth=2, alpha=0.7,
               label='Unhealthy Threshold (55.4 µg/m³)')
    
    # Add shaded region between thresholds using fill_between
    ax.fill_between(dates, 35, 55.4,
                    color='orange', alpha=0.15,
                    label='Unhealthy for Sensitive Groups')
    
    # Formatting
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('PM2.5 Concentration (µg/m³)', fontsize=14, fontweight='bold')
    ax.set_title('PM2.5 Air Quality Time Series - 2024\n'
                 'Daily Values and 7-Day Rolling Averages with EPA Thresholds',
                 fontsize=16, fontweight='bold', pad=20)
    
    # Configure legend - place outside plot area
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1),
              ncol=1, borderaxespad=0, frameon=True,
              fontsize=10)
    
    # Grid for readability
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    # Rotate x-axis labels
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Set y-axis limits to focus on relevant range
    ax.set_ylim(0, max(df['value'].max() * 1.1, 100))
    
    # Tight layout to prevent label cutoff
    plt.tight_layout()
    
    # Save figure
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_path}")
    
    # Also save as PNG for easy viewing
    png_path = output_path.replace('.pdf', '.png')
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    print(f"Figure also saved to: {png_path}")
    
    plt.close()


def main():
    """Main execution function."""
    # Determine paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_path = os.path.join(project_dir, 'data', 'all_cities_pm25.csv')
    output_path = os.path.join(project_dir, 'figures', 'timeseries_detailed.pdf')
    
    # Check if data file exists
    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        print("Please run fetch_data.py first to download the data.")
        sys.exit(1)
    
    # Load data
    print(f"Loading data from {data_path}...")
    df = load_data(data_path)
    print(f"Loaded {len(df)} records for {df['city'].nunique()} cities")
    
    # Create plot
    print("Creating enhanced time series plot...")
    plot_enhanced_timeseries(df, output_path)
    
    print("Done!")


if __name__ == '__main__':
    main()

