"""
Create simple initial visualization for proposal
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

CITIES = ['Los Angeles', 'Fresno', 'Phoenix', 'Denver', 'Salt Lake City', 'Pittsburgh']
CITY_COLORS = {
    'Los Angeles': '#d62728',
    'Fresno': '#ff7f0e', 
    'Phoenix': '#8c564b',
    'Denver': '#9467bd',
    'Salt Lake City': '#2ca02c',
    'Pittsburgh': '#1f77b4'
}

def load_data():
    """Load PM2.5 data"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '..', 'data', 'all_cities_pm25.csv')
    pm25_data = pd.read_csv(data_file)
    pm25_data['date'] = pd.to_datetime(pm25_data['date'])
    return pm25_data

def create_plot(pm25_data, output_file=None):
    """Create simple comparison plot"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for city in CITIES:
        city_data = pm25_data[pm25_data['city'] == city]
        if not city_data.empty:
            ax.plot(city_data['date'], city_data['value'], 
                   linewidth=1.5, alpha=0.8, label=city, 
                   color=CITY_COLORS.get(city, 'gray'))
    
    ax.axhline(y=35, color='red', linestyle='--', linewidth=2, 
               label='EPA Standard (35 µg/m³)', alpha=0.8)
    
    ax.set_ylabel('PM2.5 (µg/m³)', fontweight='bold')
    ax.set_xlabel('Date (2024)', fontweight='bold')
    ax.set_title('Air Quality Comparison Across US Cities (2024)', fontweight='bold')
    ax.legend(loc='upper right', ncol=3)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0, top=85)
    
    ax.set_xlim(pd.Timestamp('2024-01-01'), pd.Timestamp('2024-12-31'))
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    
    plt.tight_layout()
    
    # Set output file if not provided
    if output_file is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_file = os.path.join(script_dir, '..', 'figures', 'air_quality_timeseries.png')
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_file}")

if __name__ == "__main__":
    print("Loading data...")
    pm25_data = load_data()
    
    print("Creating plot...")
    create_plot(pm25_data)
    
    print("Done!")