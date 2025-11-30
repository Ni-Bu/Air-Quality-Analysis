"""
Trend Analysis Module for Air Quality Data

This module provides functions for analyzing temporal trends in air quality
data, including linear regression, seasonal patterns, and monthly statistics.

Functions:
    calculate_linear_trend: Perform linear regression on time series data
    calculate_seasonal_average: Calculate seasonal statistics
    calculate_monthly_statistics: Aggregate data by month
"""

from typing import Union, Tuple
import numpy as np
import pandas as pd
from scipy import stats


def calculate_linear_trend(
    dates: Union[pd.Series, np.ndarray],
    values: Union[pd.Series, np.ndarray, list]
) -> Tuple[float, float, float, float]:
    """
    Calculate linear trend using least squares regression.

    Performs linear regression on time series data to determine trend direction
    and strength. Returns slope, intercept, R-squared, and p-value.

    Parameters
    ----------
    dates : pd.Series or np.ndarray
        Date/time values (will be converted to numeric ordinal values)
    values : pd.Series, np.ndarray, or list
        Corresponding data values (e.g., PM2.5 concentrations)

    Returns
    -------
    tuple of (float, float, float, float)
        slope : Rate of change per day
        intercept : Y-intercept of trend line
        r_squared : Coefficient of determination (0-1)
        p_value : Statistical significance of slope

    Raises
    ------
    ValueError
        If dates and values have different lengths or contain invalid data

    Examples
    --------
    >>> dates = pd.date_range('2024-01-01', periods=5)
    >>> values = [10, 12, 11, 13, 15]
    >>> slope, intercept, r2, pval = calculate_linear_trend(dates, values)
    >>> print(f"Slope: {slope:.3f}, R²: {r2:.3f}")
    """
    # Convert to numpy arrays
    values_array = np.array(values, dtype=float)

    # Convert dates to ordinal (days since epoch)
    if isinstance(dates, pd.Series):
        dates_numeric = pd.to_datetime(dates).map(pd.Timestamp.toordinal)
        dates_array = np.array(dates_numeric, dtype=float)
    elif isinstance(dates, np.ndarray):
        if dates.dtype.kind == 'M':  # numpy datetime64
            dates_array = dates.astype('datetime64[D]').astype(float)
        else:
            dates_array = np.array(dates, dtype=float)
    else:
        dates_array = np.array(dates, dtype=float)

    # Validate inputs
    if len(dates_array) != len(values_array):
        raise ValueError(
            f"dates and values must have same length: "
            f"{len(dates_array)} != {len(values_array)}"
        )

    if len(dates_array) < 2:
        raise ValueError(
            "At least 2 data points required for linear regression"
        )

    # Remove NaN values
    mask = ~(np.isnan(dates_array) | np.isnan(values_array))
    dates_clean = dates_array[mask]
    values_clean = values_array[mask]

    if len(dates_clean) < 2:
        raise ValueError(
            "At least 2 valid (non-NaN) data points required"
        )

    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        dates_clean, values_clean
    )

    r_squared = r_value ** 2

    return float(slope), float(intercept), float(r_squared), float(p_value)


def calculate_seasonal_average(
    df: pd.DataFrame,
    season: str
) -> float:
    """
    Calculate average value for a specific season.

    Filters data by meteorological season and computes mean. Seasons are
    defined as: Winter (Dec-Feb), Spring (Mar-May), Summer (Jun-Aug),
    Fall (Sep-Nov).

    Parameters
    ----------
    df : pd.DataFrame
        Data with 'date' and 'value' columns (lowercase)
    season : str
        Season name: 'winter', 'spring', 'summer', or 'fall' (case-insensitive)

    Returns
    -------
    float
        Mean value for the specified season

    Raises
    ------
    ValueError
        If season name is invalid or required columns are missing
    KeyError
        If 'date' or 'value' columns not found in dataframe

    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'date': pd.date_range('2024-01-01', periods=365),
    ...     'value': np.random.uniform(5, 20, 365)
    ... })
    >>> winter_avg = calculate_seasonal_average(df, 'winter')
    """
    # Validate inputs
    if 'date' not in df.columns or 'value' not in df.columns:
        raise KeyError(
            "DataFrame must contain 'date' and 'value' columns"
        )

    season_lower = season.lower()
    valid_seasons = ['winter', 'spring', 'summer', 'fall', 'autumn']

    if season_lower not in valid_seasons:
        raise ValueError(
            f"Invalid season '{season}'. "
            f"Must be one of: winter, spring, summer, fall"
        )

    # Handle 'autumn' as alias for 'fall'
    if season_lower == 'autumn':
        season_lower = 'fall'

    # Ensure date column is datetime
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])

    # Extract month
    df_copy['month'] = df_copy['date'].dt.month

    # Define seasonal month ranges
    season_months = {
        'winter': [12, 1, 2],
        'spring': [3, 4, 5],
        'summer': [6, 7, 8],
        'fall': [9, 10, 11]
    }

    # Filter by season
    months = season_months[season_lower]
    seasonal_data = df_copy[df_copy['month'].isin(months)]

    if len(seasonal_data) == 0:
        raise ValueError(
            f"No data found for season '{season}'"
        )

    # Calculate mean, excluding NaN
    mean_value = seasonal_data['value'].mean()

    return float(mean_value)


def calculate_monthly_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly aggregated statistics.

    Groups data by month and calculates mean, median, min, max, and count
    for each month.

    Parameters
    ----------
    df : pd.DataFrame
        Data with 'date' and 'value' columns (lowercase)

    Returns
    -------
    pd.DataFrame
        Monthly statistics with columns:
        - month: Month number (1-12)
        - mean: Monthly average
        - median: Monthly median
        - min: Monthly minimum
        - max: Monthly maximum
        - count: Number of observations

    Raises
    ------
    KeyError
        If 'date' or 'value' columns not found in dataframe

    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'date': pd.date_range('2024-01-01', periods=365),
    ...     'value': np.random.uniform(5, 20, 365)
    ... })
    >>> monthly_stats = calculate_monthly_statistics(df)
    >>> print(monthly_stats[['month', 'mean']])
    """
    # Validate inputs
    if 'date' not in df.columns or 'value' not in df.columns:
        raise KeyError(
            "DataFrame must contain 'date' and 'value' columns"
        )

    # Ensure date column is datetime
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])

    # Extract month
    df_copy['month'] = df_copy['date'].dt.month

    # Calculate statistics by month
    monthly_stats = df_copy.groupby('month')['value'].agg([
        ('mean', 'mean'),
        ('median', 'median'),
        ('min', 'min'),
        ('max', 'max'),
        ('count', 'count')
    ]).reset_index()

    return monthly_stats
