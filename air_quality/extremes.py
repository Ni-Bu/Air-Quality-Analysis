"""
Extreme value analysis module for PM2.5 air quality data.

This module provides functions for identifying extreme air quality events
using different methodologies: threshold-based, percentile-based, and
consecutive exceedance analysis.
"""

import numpy as np
import pandas as pd
from typing import Union


def identify_extremes_threshold(
    df: pd.DataFrame,
    threshold: float
) -> pd.DataFrame:
    """
    Identify days where PM2.5 values exceed a specific threshold.

    Args:
        df: DataFrame with 'Date' and 'PM2.5' columns
        threshold: PM2.5 threshold value in μg/m³

    Returns:
        DataFrame containing only rows where PM2.5 exceeds threshold,
        sorted by PM2.5 value in descending order

    Raises:
        ValueError: If threshold is negative or DataFrame is empty
        KeyError: If required columns are missing

    Examples:
        >>> df = pd.DataFrame({
        ...     'Date': pd.date_range('2024-01-01', periods=5),
        ...     'PM2.5': [10.0, 40.0, 30.0, 50.0, 20.0]
        ... })
        >>> result = identify_extremes_threshold(df, 35.0)
        >>> len(result)
        2
    """
    if threshold < 0:
        raise ValueError("Threshold must be non-negative")

    if df.empty:
        raise ValueError("DataFrame cannot be empty")

    required_columns = ['Date', 'PM2.5']
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' not found in DataFrame")

    # Filter for values exceeding threshold
    extremes = df[df['PM2.5'] > threshold].copy()

    # Sort by PM2.5 value in descending order
    extremes = extremes.sort_values('PM2.5', ascending=False)

    return extremes


def identify_extremes_percentile(
    df: pd.DataFrame,
    percentile: float
) -> pd.DataFrame:
    """
    Identify extreme days based on percentile threshold.

    Args:
        df: DataFrame with 'Date' and 'PM2.5' columns
        percentile: Percentile threshold (0-100). Days above this
                   percentile are considered extreme

    Returns:
        DataFrame containing only rows in the extreme percentile,
        sorted by PM2.5 value in descending order

    Raises:
        ValueError: If percentile is not between 0 and 100 or
                   DataFrame is empty
        KeyError: If required columns are missing

    Examples:
        >>> df = pd.DataFrame({
        ...     'Date': pd.date_range('2024-01-01', periods=10),
        ...     'PM2.5': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        ... })
        >>> result = identify_extremes_percentile(df, 90)
        >>> len(result)
        1
    """
    if not 0 <= percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100")

    if df.empty:
        raise ValueError("DataFrame cannot be empty")

    required_columns = ['Date', 'PM2.5']
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' not found in DataFrame")

    # Calculate percentile threshold
    threshold_value = np.percentile(df['PM2.5'].dropna(), percentile)

    # Filter for values above percentile threshold
    extremes = df[df['PM2.5'] > threshold_value].copy()

    # Sort by PM2.5 value in descending order
    extremes = extremes.sort_values('PM2.5', ascending=False)

    return extremes


def identify_consecutive_exceedances(
    df: pd.DataFrame,
    threshold: float
) -> pd.DataFrame:
    """
    Identify consecutive sequences of days exceeding a threshold.

    This function finds all periods where PM2.5 values exceed a threshold
    for multiple consecutive days, which is important for understanding
    sustained air quality episodes.

    Args:
        df: DataFrame with 'Date' and 'PM2.5' columns, should be
            sorted by Date
        threshold: PM2.5 threshold value in μg/m³

    Returns:
        DataFrame with columns:
            - 'start_date': Start date of exceedance period
            - 'end_date': End date of exceedance period
            - 'duration': Number of consecutive days
            - 'max_pm25': Maximum PM2.5 during the period
            - 'mean_pm25': Mean PM2.5 during the period

    Raises:
        ValueError: If threshold is negative or DataFrame is empty
        KeyError: If required columns are missing

    Examples:
        >>> df = pd.DataFrame({
        ...     'Date': pd.date_range('2024-01-01', periods=7),
        ...     'PM2.5': [10, 40, 45, 50, 15, 60, 65]
        ... })
        >>> result = identify_consecutive_exceedances(df, 35)
        >>> len(result)
        2
    """
    if threshold < 0:
        raise ValueError("Threshold must be non-negative")

    if df.empty:
        raise ValueError("DataFrame cannot be empty")

    required_columns = ['Date', 'PM2.5']
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Required column '{col}' not found in DataFrame")

    # Create a copy and sort by date
    df_sorted = df.sort_values('Date').copy()

    # Create boolean mask for exceedances
    exceeds = df_sorted['PM2.5'] > threshold

    # Find consecutive sequences
    # When exceeds changes from False to True, it's a new sequence start
    # When it changes from True to False, it's a sequence end
    sequence_starts = exceeds & ~exceeds.shift(1, fill_value=False)
    sequence_changes = exceeds != exceeds.shift(1, fill_value=False)

    # Assign sequence IDs
    sequence_ids = sequence_changes.cumsum()

    # Only keep sequences where exceedance occurred
    df_sorted['sequence_id'] = sequence_ids
    df_sorted['exceeds'] = exceeds

    exceedance_sequences = df_sorted[df_sorted['exceeds']].copy()

    if exceedance_sequences.empty:
        # Return empty DataFrame with correct columns
        return pd.DataFrame(columns=[
            'start_date', 'end_date', 'duration', 'max_pm25', 'mean_pm25'
        ])

    # Group by sequence_id and calculate statistics
    results = []
    for seq_id, group in exceedance_sequences.groupby('sequence_id'):
        results.append({
            'start_date': group['Date'].iloc[0],
            'end_date': group['Date'].iloc[-1],
            'duration': len(group),
            'max_pm25': group['PM2.5'].max(),
            'mean_pm25': group['PM2.5'].mean()
        })

    result_df = pd.DataFrame(results)

    # Sort by duration (longest first), then by max_pm25
    result_df = result_df.sort_values(
        ['duration', 'max_pm25'],
        ascending=[False, False]
    )

    return result_df.reset_index(drop=True)

