"""
Fetch air quality data from EPA Air Quality System (AQS)
Data source: https://www.epa.gov/outdoor-air-quality-data
"""

import requests
import pandas as pd
import os
import zipfile
import io

# City definitions: (State Code, County Codes, City Name)
CITIES = {
    'Los Angeles': ('06', ['037'], 'Los Angeles, CA'),
    'Fresno': ('06', ['019'], 'Fresno, CA'),
    'Phoenix': ('04', ['013'], 'Phoenix, AZ'),
    'Denver': ('08', ['031'], 'Denver, CO'),
    'Salt Lake City': ('49', ['035'], 'Salt Lake City, UT'),
    'Pittsburgh': ('42', ['003'], 'Pittsburgh, PA')
}

def download_epa_data(year, parameter_code):
    """Download EPA AQS data for a specific year and parameter"""
    base_url = "https://aqs.epa.gov/aqsweb/airdata"
    filename = f"daily_{parameter_code}_{year}.zip"
    url = f"{base_url}/{filename}"
    
    print(f"Downloading {filename}...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            csv_filename = f"daily_{parameter_code}_{year}.csv"
            with zip_file.open(csv_filename) as csv_file:
                df = pd.read_csv(csv_file)
        
        print(f"Downloaded {len(df)} records")
        return df
        
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
        return None

def process_pollutant_data(df, pollutant_name, parameter_code, state_code, county_codes, city_name):
    """Process and filter data for a specific city and pollutant"""
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Convert state and county codes to strings for proper comparison
    df['State Code'] = df['State Code'].astype(str).str.zfill(2)
    df['County Code'] = df['County Code'].astype(str).str.zfill(3)
    
    # Filter by state and county
    city_data = df[
        (df['State Code'] == state_code) & 
        (df['County Code'].isin(county_codes))
    ].copy()
    
    if city_data.empty:
        print(f"No data found for {city_name} (State: {state_code}, Counties: {county_codes})")
        return pd.DataFrame()
    
    # Calculate daily averages
    daily_avg = city_data.groupby('Date Local')['Arithmetic Mean'].mean().reset_index()
    daily_avg['city'] = city_name
    daily_avg['pollutant'] = pollutant_name
    daily_avg['date'] = pd.to_datetime(daily_avg['Date Local'])
    daily_avg['value'] = daily_avg['Arithmetic Mean']
    
    # Keep only necessary columns
    result = daily_avg[['date', 'city', 'pollutant', 'value']].copy()
    
    print(f"Processed {len(result)} days for {city_name} {pollutant_name}")
    return result

def main():
    """Main function to download and process all data"""
    year = 2024
    
    # Download PM2.5 data
    print("Downloading PM2.5 data...")
    pm25_raw = download_epa_data(year, '88101')
    
    if pm25_raw is not None:
        # Process PM2.5 for all cities
        pm25_all = pd.DataFrame()
        
        for city_name, (state_code, county_codes, _) in CITIES.items():
            city_data = process_pollutant_data(
                pm25_raw, 'PM2.5', '88101', state_code, county_codes, city_name
            )
            pm25_all = pd.concat([pm25_all, city_data], ignore_index=True)
        
        # Save PM2.5 data
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, 'all_cities_pm25.csv')
        pm25_all.to_csv(output_file, index=False)
        print(f"Saved PM2.5 data: {len(pm25_all)} records")
    
    print("Data download complete!")

if __name__ == "__main__":
    main()