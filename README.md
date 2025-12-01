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

#### PM2.5 Distribution Histogram
```bash
cd scripts
python3 plot_distribution.py
```
*Generates histogram showing overall PM2.5 distribution across all cities with EPA thresholds and summary statistics*

#### Trend Analysis with Linear Fits
```bash
cd scripts
python3 plot_trends.py
```
*Generates scatter plots with fitted linear trend lines for each city, showing temporal trends in PM2.5 values over 2024 with R² values and slope annotations*

#### Sensitivity Analysis
```bash
cd scripts
python3 plot_sensitivity.py
```
*Generates multi-line plot showing how extreme event counts vary with threshold definitions (15-40 μg/m³), demonstrating robustness of findings to threshold choice*

### Demo Notebook
Explore the air quality analysis modules interactively:
```bash
jupyter notebook analysis_demo.ipynb
```

The demo notebook provides a complete analysis workflow that demonstrates:
- **Statistics module:** mean calculations, rolling averages, exceedance counts, and AQI conversions
- **Extremes module:** threshold-based, percentile-based, and consecutive exceedance detection
- **Trends module:** linear trend analysis, seasonal patterns, and monthly statistics
- **Visualization workflow:** The notebook uses the standalone plotting scripts from `scripts/` to generate publication-quality figures
  - Time series with 7-day rolling averages and EPA thresholds (via `plot_timeseries.py`)
  - Statistical summary box plots (via `plot_statistics.py`)
  - Extreme events comparison charts (via `plot_extremes.py`)
  - PM2.5 distribution histograms (via `plot_distribution.py`)

This demonstrates the modular design where analysis functions and visualization scripts can be reused across different workflows.

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
- `scripts/plot_distribution.py` - Generate PM2.5 distribution histogram with EPA thresholds
- `scripts/plot_trends.py` - Generate trend analysis scatter plots with fitted linear regression lines
- `scripts/plot_sensitivity.py` - Generate sensitivity analysis showing robustness to threshold choice
- `air_quality/statistics.py` - Statistical analysis functions (mean, rolling average, exceedance counts, AQI calculation)
- `air_quality/extremes.py` - Extreme value identification (threshold-based, percentile-based, consecutive exceedances)
- `air_quality/trends.py` - Trend analysis functions (linear regression, seasonal patterns, monthly statistics)
- `air_quality/plotting.py` - Plotting utilities (styles, colors, subplot helpers)
- `tests/test_statistics.py` - Tests for statistics module
- `tests/test_extremes.py` - Tests for extremes module
- `tests/test_trends.py` - Tests for trends module

## Generated Files
*Note: The following files are created when scripts are executed and are not tracked in git:*
- `data/all_cities_pm25.csv` - Processed PM2.5 data (created by fetch_data.py)
- `figures/air_quality_timeseries.pdf` - Basic time series plot (created by simple_plot.py)
- `figures/timeseries_detailed.pdf` - Enhanced time series with rolling averages and thresholds (created by plot_timeseries.py)
- `figures/statistical_summary.pdf` - Box plots showing PM2.5 distribution by city (created by plot_statistics.py)
- `figures/extreme_events.pdf` - Grouped bar chart comparing exceedance counts (created by plot_extremes.py)
- `figures/pm25_distribution.pdf` - Histogram showing overall PM2.5 distribution with thresholds (created by plot_distribution.py)
- `figures/trend_analysis.pdf` - Scatter plots with linear trend lines showing temporal trends (created by plot_trends.py)
- `figures/sensitivity_analysis.pdf` - Multi-line plot showing sensitivity to threshold definitions (created by plot_sensitivity.py)