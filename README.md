# Air Quality Analysis CMSC 6950 Project

## Overview
Analysis of PM2.5 air quality data across six US cities in 2024, focusing on extreme value statistics and EPA standard compliance.

## Dataset
- **Source:** EPA Air Quality System (AQS)
- **Cities:** Los Angeles, Fresno, Phoenix, Denver, Salt Lake City, Pittsburgh
- **Time Period:** 2024
- **Pollutant:** PM2.5 (daily averages)

## Setup
```bash
pip install -r requirements.txt
```

## Usage

### Download Data
```bash
cd scripts
python3 fetch_data.py
```

### Generate Plot
```bash
cd scripts
python3 simple_plot.py
```

## Files
- `scripts/fetch_data.py` - Download EPA AQS data
- `scripts/simple_plot.py` - Generate initial visualization

## Generated Files
*Note: The following files are created when scripts are executed and are not tracked in git:*
- `data/all_cities_pm25.csv` - Processed PM2.5 data (created by fetch_data.py)
- `figures/air_quality_timeseries.png` - Initial plot (created by simple_plot.py)
