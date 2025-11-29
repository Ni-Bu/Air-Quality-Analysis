"""Tests for the extremes module."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from air_quality.extremes import (
    identify_extremes_threshold,
    identify_extremes_percentile,
    identify_consecutive_exceedances
)


# Tests for identify_extremes_threshold
@pytest.mark.parametrize("threshold,expected_count", [
    (50.0, 5),  # Basic: values > 50
    (40.0, 6),  # More values
    (150.0, 0),  # No exceedances
    (0.0, 10),  # All values exceed
])
def test_threshold_basic_counts(threshold, expected_count):
    """Test threshold identification with different threshold values."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=10),
        'PM2.5': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    })
    result = identify_extremes_threshold(df, threshold)
    assert len(result) == expected_count
    if expected_count > 0:
        assert all(result['PM2.5'] > threshold)


def test_threshold_sorted_descending():
    """Test that results are sorted by PM2.5 descending."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=10),
        'PM2.5': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    })
    result = identify_extremes_threshold(df, 40.0)
    pm25_values = result['PM2.5'].values
    assert all(pm25_values[i] >= pm25_values[i+1]
               for i in range(len(pm25_values)-1))


def test_threshold_exact_value_excluded():
    """Test that exact threshold value is NOT included (> not >=)."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=10),
        'PM2.5': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    })
    result = identify_extremes_threshold(df, 50.0)
    assert 50.0 not in result['PM2.5'].values


def test_threshold_negative_value():
    """Test that negative threshold raises ValueError."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=5),
        'PM2.5': [10, 20, 30, 40, 50]
    })
    with pytest.raises(ValueError, match="Threshold must be non-negative"):
        identify_extremes_threshold(df, -10.0)


def test_threshold_empty_dataframe():
    """Test with empty DataFrame."""
    empty_df = pd.DataFrame({'Date': [], 'PM2.5': []})
    with pytest.raises(ValueError, match="DataFrame cannot be empty"):
        identify_extremes_threshold(empty_df, 35.0)


def test_threshold_missing_columns():
    """Test with missing required columns."""
    df = pd.DataFrame({'Date': [datetime(2024, 1, 1)]})
    with pytest.raises(KeyError, match="Required column 'PM2.5'"):
        identify_extremes_threshold(df, 35.0)


# Tests for identify_extremes_percentile
@pytest.mark.parametrize("percentile,expected_count", [
    (90, 1),  # 90th percentile
    (50, 5),  # 50th percentile (median)
    (70, 3),  # 70th percentile
])
def test_percentile_basic(percentile, expected_count):
    """Test percentile identification with different percentiles."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=10),
        'PM2.5': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    })
    result = identify_extremes_percentile(df, percentile)
    assert len(result) == expected_count


def test_percentile_sorted_descending():
    """Test that results are sorted by PM2.5 descending."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=10),
        'PM2.5': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    })
    result = identify_extremes_percentile(df, 70)
    pm25_values = result['PM2.5'].values
    assert all(pm25_values[i] >= pm25_values[i+1]
               for i in range(len(pm25_values)-1))


@pytest.mark.parametrize("percentile", [
    -10,  # Below 0
    150,  # Above 100
])
def test_percentile_invalid(percentile):
    """Test that invalid percentiles raise ValueError."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=5),
        'PM2.5': [10, 20, 30, 40, 50]
    })
    with pytest.raises(ValueError,
                       match="Percentile must be between 0 and 100"):
        identify_extremes_percentile(df, percentile)


def test_percentile_empty_dataframe():
    """Test with empty DataFrame."""
    empty_df = pd.DataFrame({'Date': [], 'PM2.5': []})
    with pytest.raises(ValueError, match="DataFrame cannot be empty"):
        identify_extremes_percentile(empty_df, 90)


def test_percentile_with_nan():
    """Test that NaN values are handled correctly."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=5),
        'PM2.5': [10.0, 20.0, np.nan, 40.0, 50.0]
    })
    result = identify_extremes_percentile(df, 75)
    assert len(result) >= 0
    assert not result['PM2.5'].isna().any()


# Tests for identify_consecutive_exceedances
@pytest.mark.parametrize("pm25_values,threshold,expected_sequences", [
    # Two separate sequences
    ([10, 15, 50, 55, 60, 20, 25, 45, 48, 52, 55, 30], 40, 2),
    # No exceedances
    ([10, 20, 30, 40, 50], 150, 0),
    # All exceedances (one long sequence)
    ([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], 0, 1),
    # Alternating (single-day sequences)
    ([10, 50, 10, 50, 10, 50, 10], 40, 3),
])
def test_consecutive_basic(pm25_values, threshold, expected_sequences):
    """Test consecutive exceedance identification."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=len(pm25_values)),
        'PM2.5': pm25_values
    })
    result = identify_consecutive_exceedances(df, threshold)
    assert len(result) == expected_sequences
    if expected_sequences == 0:
        # Check that empty result has correct columns
        expected_cols = ['start_date', 'end_date', 'duration',
                         'max_pm25', 'mean_pm25']
        assert all(col in result.columns for col in expected_cols)


def test_consecutive_dates_correct():
    """Test that start and end dates are correct."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=7),
        'PM2.5': [10, 40, 45, 50, 15, 60, 65]
    })
    result = identify_consecutive_exceedances(df, 40)
    for _, row in result.iterrows():
        date_diff = (row['end_date'] - row['start_date']).days + 1
        assert date_diff == row['duration']


def test_consecutive_sorted_by_duration():
    """Test that results are sorted by duration descending."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=12),
        'PM2.5': [10, 15, 50, 55, 60, 20, 25, 45, 48, 52, 55, 30]
    })
    result = identify_consecutive_exceedances(df, 40)
    durations = result['duration'].values
    assert all(durations[i] >= durations[i+1]
               for i in range(len(durations)-1))


def test_consecutive_statistics():
    """Test that max and mean PM2.5 are calculated correctly."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=5),
        'PM2.5': [50, 60, 55, 70, 65]
    })
    result = identify_consecutive_exceedances(df, 40)
    assert len(result) == 1
    # Check max
    assert result.iloc[0]['max_pm25'] == 70.0
    # Check mean (should be 60)
    assert abs(result.iloc[0]['mean_pm25'] - 60.0) < 0.01
    # Max should be >= mean
    assert result.iloc[0]['max_pm25'] >= result.iloc[0]['mean_pm25']


def test_consecutive_negative_threshold():
    """Test that negative threshold raises ValueError."""
    df = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=5),
        'PM2.5': [10, 20, 30, 40, 50]
    })
    with pytest.raises(ValueError, match="Threshold must be non-negative"):
        identify_consecutive_exceedances(df, -10)


def test_consecutive_empty_dataframe():
    """Test with empty DataFrame."""
    empty_df = pd.DataFrame({'Date': [], 'PM2.5': []})
    with pytest.raises(ValueError, match="DataFrame cannot be empty"):
        identify_consecutive_exceedances(empty_df, 35)
