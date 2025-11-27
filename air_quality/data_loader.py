"""Data loading and filtering utilities for air quality analysis.

This module provides functions for loading PM2.5 data from CSV files
and filtering by city, date range, and other criteria.
"""

from typing import List, Optional
import pandas as pd


def load_pm25_data(filepath: str) -> pd.DataFrame:
    """Load PM2.5 data from a CSV file.

    Args:
        filepath: Path to the CSV file containing PM2.5 data.
            Expected columns: date, city, pollutant, value

    Returns:
        DataFrame with PM2.5 data, with date column converted to datetime.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If required columns are missing from the CSV.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Data file not found: {filepath}"
        ) from e

    # Validate required columns
    required_columns = ['date', 'city', 'pollutant', 'value']
    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_columns)}"
        )

    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])

    return df


def filter_by_city(df: pd.DataFrame, city_name: str) -> pd.DataFrame:
    """Filter DataFrame for a specific city.

    Args:
        df: DataFrame containing air quality data.
        city_name: Name of the city to filter for.

    Returns:
        Filtered DataFrame containing only data for the specified city.

    Raises:
        ValueError: If the city is not found in the DataFrame.
    """
    if 'city' not in df.columns:
        raise ValueError("DataFrame must contain 'city' column")

    filtered_df = df[df['city'] == city_name].copy()

    if filtered_df.empty:
        available_cities = df['city'].unique().tolist()
        raise ValueError(
            f"City '{city_name}' not found. "
            f"Available cities: {', '.join(available_cities)}"
        )

    return filtered_df


def filter_by_date_range(
    df: pd.DataFrame,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """Filter DataFrame by date range.

    Args:
        df: DataFrame containing air quality data with 'date' column.
        start_date: Start date in format 'YYYY-MM-DD'. If None, no lower
            bound is applied.
        end_date: End date in format 'YYYY-MM-DD'. If None, no upper
            bound is applied.

    Returns:
        Filtered DataFrame containing only data within the date range.

    Raises:
        ValueError: If date column is missing or dates are invalid.
    """
    if 'date' not in df.columns:
        raise ValueError("DataFrame must contain 'date' column")

    filtered_df = df.copy()

    # Apply start date filter if provided
    if start_date is not None:
        try:
            start_dt = pd.to_datetime(start_date)
            filtered_df = filtered_df[filtered_df['date'] >= start_dt]
        except Exception as e:
            raise ValueError(
                f"Invalid start_date format: {start_date}. "
                f"Expected format: YYYY-MM-DD"
            ) from e

    # Apply end date filter if provided
    if end_date is not None:
        try:
            end_dt = pd.to_datetime(end_date)
            filtered_df = filtered_df[filtered_df['date'] <= end_dt]
        except Exception as e:
            raise ValueError(
                f"Invalid end_date format: {end_date}. "
                f"Expected format: YYYY-MM-DD"
            ) from e

    return filtered_df


def get_cities_list(df: pd.DataFrame) -> List[str]:
    """Get a sorted list of unique cities in the DataFrame.

    Args:
        df: DataFrame containing air quality data with 'city' column.

    Returns:
        Sorted list of unique city names.

    Raises:
        ValueError: If the 'city' column is not present in the DataFrame.
    """
    if 'city' not in df.columns:
        raise ValueError("DataFrame must contain 'city' column")

    cities = sorted(df['city'].unique().tolist())
    return cities

