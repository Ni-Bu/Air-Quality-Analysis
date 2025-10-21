"""
Fetch air quality data from EPA Air Quality System (AQS)
Data source: https://www.epa.gov/outdoor-air-quality-data
"""

import requests
import pandas as pd
import zipfile
import io

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

def main():
    year = 2024
    
    # Download PM2.5 data
    print("Downloading PM2.5 data...")
    pm25_raw = download_epa_data(year, '88101')

    print(pm25_raw.head())


if __name__ == "__main__":
    main()