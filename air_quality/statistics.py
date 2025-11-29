"""Statistical functions for air quality analysis.

This module provides statistical analysis functions for PM2.5 data,
including rolling averages, exceedance counting, and AQI calculations.
All functions use NumPy arrays for efficient computation.
"""

from typing import Union
import numpy as np


def calculate_daily_mean(values: Union[np.ndarray, list]) -> float:
    """Calculate the mean of daily values using NumPy.

    Args:
        values: Array or list of numerical values.

    Returns:
        The arithmetic mean of the values.

    Raises:
        ValueError: If the input array is empty.

    Examples:
        >>> calculate_daily_mean([10, 20, 30])
        20.0
        >>> calculate_daily_mean(np.array([5.5, 10.5, 15.5]))
        10.5
    """
    values_array = np.asarray(values, dtype=float)

    if values_array.size == 0:
        raise ValueError("Cannot calculate mean of empty array")

    # Remove NaN values
    values_clean = values_array[~np.isnan(values_array)]

    if values_clean.size == 0:
        raise ValueError("Cannot calculate mean: all values are NaN")

    return float(np.mean(values_clean))


def calculate_rolling_average(
    values: Union[np.ndarray, list],
    window: int = 7
) -> np.ndarray:
    """Calculate rolling (moving) average with specified window size.

    Args:
        values: Array or list of numerical values.
        window: Size of the rolling window (default: 7 for weekly average).

    Returns:
        NumPy array of rolling averages. The first (window-1) values
        will be NaN since there aren't enough preceding values.

    Raises:
        ValueError: If window size is less than 1 or greater than array
            length.

    Examples:
        >>> calculate_rolling_average([1, 2, 3, 4, 5], window=3)
        array([nan, nan,  2.,  3.,  4.])
    """
    values_array = np.asarray(values, dtype=float)

    if window < 1:
        raise ValueError("Window size must be at least 1")

    if window > len(values_array):
        raise ValueError(
            f"Window size ({window}) cannot be larger than "
            f"array length ({len(values_array)})"
        )

    # Use NumPy convolve for efficient rolling average
    # Create output array initialized with NaN
    result = np.full(len(values_array), np.nan)

    # Calculate rolling average starting from index (window-1)
    for i in range(window - 1, len(values_array)):
        window_values = values_array[i - window + 1:i + 1]
        # Only calculate if no NaN values in window
        if not np.any(np.isnan(window_values)):
            result[i] = np.mean(window_values)

    return result


def calculate_exceedance_count(
    values: Union[np.ndarray, list],
    threshold: float
) -> int:
    """Count the number of values exceeding a threshold.

    Args:
        values: Array or list of numerical values.
        threshold: Threshold value to compare against.

    Returns:
        Integer count of values strictly greater than the threshold.

    Examples:
        >>> calculate_exceedance_count([10, 20, 30, 40], threshold=25)
        2
        >>> calculate_exceedance_count([5, 10, 15], threshold=20)
        0
    """
    values_array = np.asarray(values, dtype=float)

    # Remove NaN values before counting
    values_clean = values_array[~np.isnan(values_array)]

    # Count values exceeding threshold
    exceedance_count = np.sum(values_clean > threshold)

    return int(exceedance_count)


def calculate_aqi(pm25_value: float) -> dict:
    """Convert PM2.5 concentration to Air Quality Index (AQI) category.

    Uses EPA breakpoints for PM2.5 to calculate AQI value and category.
    This is the "meaningful function" for the project, providing health
    context interpretation of PM2.5 measurements.

    Args:
        pm25_value: PM2.5 concentration in µg/m³.

    Returns:
        Dictionary containing:
            - 'aqi': Numerical AQI value (0-500+)
            - 'category': AQI category name
            - 'color': Hex color code for visualization
            - 'health_message': Brief health impact message

    Raises:
        ValueError: If pm25_value is negative or NaN.

    Examples:
        >>> result = calculate_aqi(12.0)
        >>> result['category']
        'Good'
        >>> result = calculate_aqi(55.5)
        >>> result['category']
        'Unhealthy for Sensitive Groups'

    Notes:
        EPA PM2.5 AQI Breakpoints:
        - 0.0-12.0: Good (0-50 AQI)
        - 12.1-35.4: Moderate (51-100 AQI)
        - 35.5-55.4: Unhealthy for Sensitive Groups (101-150 AQI)
        - 55.5-150.4: Unhealthy (151-200 AQI)
        - 150.5-250.4: Very Unhealthy (201-300 AQI)
        - 250.5+: Hazardous (301-500 AQI)
    """
    if np.isnan(pm25_value) or pm25_value < 0:
        raise ValueError(
            f"Invalid PM2.5 value: {pm25_value}. "
            f"Must be non-negative number."
        )

    # EPA PM2.5 breakpoints: (C_low, C_high, I_low, I_high, category, color)
    breakpoints = [
        (0.0, 12.0, 0, 50, "Good", "#00E400",
         "Air quality is satisfactory."),
        (12.1, 35.4, 51, 100, "Moderate", "#FFFF00",
         "Acceptable for most, but sensitive groups may be affected."),
        (35.5, 55.4, 101, 150, "Unhealthy for Sensitive Groups", "#FF7E00",
         "Sensitive groups may experience health effects."),
        (55.5, 150.4, 151, 200, "Unhealthy", "#FF0000",
         "Everyone may begin to experience health effects."),
        (150.5, 250.4, 201, 300, "Very Unhealthy", "#8F3F97",
         "Health alert: everyone may experience serious effects."),
        (250.5, 500.4, 301, 500, "Hazardous", "#7E0023",
         "Health warnings of emergency conditions."),
    ]

    # Find appropriate breakpoint
    for c_low, c_high, i_low, i_high, category, color, message in breakpoints:
        if c_low <= pm25_value <= c_high:
            # Linear interpolation formula: I = [(I_high - I_low) /
            # (C_high - C_low)] * (C - C_low) + I_low
            aqi = ((i_high - i_low) / (c_high - c_low)) * \
                  (pm25_value - c_low) + i_low
            return {
                'aqi': int(round(aqi)),
                'category': category,
                'color': color,
                'health_message': message
            }

    # If above all breakpoints, return Hazardous with max AQI
    if pm25_value > 500.4:
        return {
            'aqi': 500,
            'category': 'Hazardous',
            'color': '#7E0023',
            'health_message': (
                'Health warnings of emergency conditions. '
                'Entire population more likely to be affected.'
            )
        }

    # This shouldn't be reached if breakpoints are correct
    raise ValueError(f"Unable to calculate AQI for PM2.5 = {pm25_value}")
