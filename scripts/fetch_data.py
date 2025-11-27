"""
Fetch air quality data from EPA Air Quality System (AQS)

This module downloads daily PM2.5 air quality data from the EPA AQS
database for multiple cities and processes it into a standardized format.

Data source: https://www.epa.gov/outdoor-air-quality-data
"""

import io
import os
import zipfile
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests


# City definitions: (State Code, County Codes, City Name)
CITIES: Dict[str, Tuple[str, List[str], str]] = {
    'Los Angeles': ('06', ['037'], 'Los Angeles, CA'),
    'Fresno': ('06', ['019'], 'Fresno, CA'),
    'Phoenix': ('04', ['013'], 'Phoenix, AZ'),
    'Denver': ('08', ['031'], 'Denver, CO'),
    'Salt Lake City': ('49', ['035'], 'Salt Lake City, UT'),
    'Pittsburgh': ('42', ['003'], 'Pittsburgh, PA')
}


def download_epa_data(year: int, parameter_code: str) -> Optional[
        pd.DataFrame]:
    """
    Download EPA AQS data for a specific year and parameter.

    Args:
        year: The year of data to download.
        parameter_code: EPA parameter code (e.g., '88101' for PM2.5).

    Returns:
        DataFrame containing the downloaded data, or None if error occurs.
    """
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


def process_pollutant_data(
        df: Optional[pd.DataFrame],
        pollutant_name: str,
        parameter_code: str,
        state_code: str,
        county_codes: List[str],
        city_name: str) -> pd.DataFrame:
    """
    Process and filter data for a specific city and pollutant.

    Args:
        df: Raw EPA data DataFrame.
        pollutant_name: Name of the pollutant (e.g., 'PM2.5').
        parameter_code: EPA parameter code.
        state_code: Two-digit state FIPS code.
        county_codes: List of three-digit county FIPS codes.
        city_name: Name of the city for labeling.

    Returns:
        Processed DataFrame with columns: date, city, pollutant, value.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # Convert state and county codes to strings for comparison
    df['State Code'] = df['State Code'].astype(str).str.zfill(2)
    df['County Code'] = df['County Code'].astype(str).str.zfill(3)

    # Filter by state and county
    city_data = df[
        (df['State Code'] == state_code) &
        (df['County Code'].isin(county_codes))
    ].copy()

    if city_data.empty:
        print(
            f"No data found for {city_name} "
            f"(State: {state_code}, Counties: {county_codes})"
        )
        return pd.DataFrame()

    # Calculate daily averages
    daily_avg = (
        city_data.groupby('Date Local')['Arithmetic Mean']
        .mean()
        .reset_index()
    )
    daily_avg['city'] = city_name
    daily_avg['pollutant'] = pollutant_name
    daily_avg['date'] = pd.to_datetime(daily_avg['Date Local'])
    daily_avg['value'] = daily_avg['Arithmetic Mean']

    # Keep only necessary columns
    result = daily_avg[['date', 'city', 'pollutant', 'value']].copy()

    print(
        f"Processed {len(result)} days "
        f"for {city_name} {pollutant_name}"
    )
    return result


def main() -> None:
    """Main function to download and process all data."""
    year = 2024

    # Download PM2.5 data
    print("Downloading PM2.5 data...")
    pm25_raw = download_epa_data(year, '88101')

    if pm25_raw is not None:
        # Process PM2.5 for all cities
        pm25_all = pd.DataFrame()

        for city_name, (state_code, county_codes, _) in CITIES.items():
            city_data = process_pollutant_data(
                pm25_raw,
                'PM2.5',
                '88101',
                state_code,
                county_codes,
                city_name
            )
            pm25_all = pd.concat([pm25_all, city_data],
                                 ignore_index=True)

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
