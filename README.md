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

### Generate Figures

#### Basic Time Series Plot
```bash
cd scripts
python3 simple_plot.py
```

#### Enhanced Time Series Plot (with rolling averages and thresholds)
```bash
cd scripts
python3 plot_timeseries.py
```

#### Statistical Summary Box Plots
```bash
cd scripts
python3 plot_statistics.py
```
*Generates box plots showing PM2.5 distribution for each city*

#### Extreme Events Comparison
```bash
cd scripts
python3 plot_extremes.py
```
*Generates grouped bar chart comparing exceedance counts across cities using EPA standard and 95th percentile thresholds*

### Demo Notebook
Explore the air quality analysis modules interactively:
```bash
jupyter notebook analysis_demo.ipynb
```

The demo notebook demonstrates all module functions using the PM2.5 data:
- Statistics module (mean, rolling average, exceedance counts, AQI)
- Extremes module (threshold, percentile, consecutive exceedances)
- Trends module (linear trends, seasonal averages, monthly statistics)
- Plotting utilities (styles, colors, subplot helpers)
- Enhanced time series visualization with rolling averages
- Statistical summary box plots with outlier analysis
- Extreme events comparison with grouped bar charts

### Run Tests
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific module tests
python3 -m pytest tests/test_statistics.py -v
python3 -m pytest tests/test_extremes.py -v
```

## Files
- `scripts/fetch_data.py` - Download EPA AQS data
- `scripts/simple_plot.py` - Generate basic time series visualization
- `scripts/plot_timeseries.py` - Generate enhanced time series with rolling averages and thresholds
- `scripts/plot_statistics.py` - Generate statistical summary box plots for each city
- `scripts/plot_extremes.py` - Generate extreme events comparison bar chart
- `air_quality/statistics.py` - Statistical analysis functions (mean, rolling average, exceedance counts, AQI calculation)
- `air_quality/extremes.py` - Extreme value identification (threshold-based, percentile-based, consecutive exceedances)
- `air_quality/plotting.py` - Plotting utilities (styles, colors, subplot helpers)
- `tests/test_statistics.py` - Tests for statistics module
- `tests/test_extremes.py` - Tests for extremes module

## Generated Files
*Note: The following files are created when scripts are executed and are not tracked in git:*
- `data/all_cities_pm25.csv` - Processed PM2.5 data (created by fetch_data.py)
- `figures/air_quality_timeseries.pdf` - Basic time series plot (created by simple_plot.py)
- `figures/timeseries_detailed.pdf` - Enhanced time series with rolling averages and thresholds (created by plot_timeseries.py)
- `figures/statistical_summary.pdf` - Box plots showing PM2.5 distribution by city (created by plot_statistics.py)
- `figures/extreme_events.pdf` - Grouped bar chart comparing exceedance counts (created by plot_extremes.py)