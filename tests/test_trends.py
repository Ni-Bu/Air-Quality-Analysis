"""
Tests for trend analysis module.

Tests cover linear trend calculation, seasonal averages, and monthly statistics
with various edge cases and data scenarios.
"""

import pytest
import numpy as np
import pandas as pd
from air_quality.trends import (
    calculate_linear_trend,
    calculate_seasonal_average,
    calculate_monthly_statistics
)


# =============================================================================
# Tests for calculate_linear_trend
# =============================================================================

@pytest.mark.parametrize("dates,values,expected_slope_sign,min_r2", [
    # Perfect positive trend
    (
        pd.date_range('2024-01-01', periods=5),
        [10, 20, 30, 40, 50],
        1,  # positive slope
        0.99  # high R²
    ),
    # Perfect negative trend
    (
        pd.date_range('2024-01-01', periods=5),
        [50, 40, 30, 20, 10],
        -1,  # negative slope
        0.99  # high R²
    ),
    # Flat trend
    (
        pd.date_range('2024-01-01', periods=5),
        [25, 25, 25, 25, 25],
        0,  # zero slope (approximately)
        0.0  # low R²
    ),
])
def test_linear_trend_direction(dates, values, expected_slope_sign,
                                min_r2):
    """Test linear trend identifies correct direction and fit quality."""
    slope, intercept, r_squared, p_value = calculate_linear_trend(
        dates, values
    )

    # Check slope sign
    if expected_slope_sign > 0:
        assert slope > 0, "Expected positive slope"
    elif expected_slope_sign < 0:
        assert slope < 0, "Expected negative slope"
    else:
        assert abs(slope) < 1e-10, "Expected near-zero slope"

    # Check R² meets minimum
    assert r_squared >= min_r2, f"R² {r_squared} below minimum {min_r2}"

    # Check valid ranges
    assert 0 <= r_squared <= 1, "R² must be between 0 and 1"
    assert 0 <= p_value <= 1, "p-value must be between 0 and 1"


@pytest.mark.parametrize("dates,values", [
    # Minimum valid case
    (pd.date_range('2024-01-01', periods=2), [10, 20]),
    # Longer series
    (pd.date_range('2024-01-01', periods=100), np.linspace(5, 25, 100)),
    # With some noise
    (
        pd.date_range('2024-01-01', periods=50),
        10 + np.random.RandomState(42).randn(50) * 2
    ),
])
def test_linear_trend_valid_inputs(dates, values):
    """Test linear trend works with various valid input types."""
    slope, intercept, r_squared, p_value = calculate_linear_trend(
        dates, values
    )

    # Results should be finite numbers
    assert np.isfinite(slope)
    assert np.isfinite(intercept)
    assert np.isfinite(r_squared)
    assert np.isfinite(p_value)


def test_linear_trend_with_numpy_arrays():
    """Test linear trend works with numpy arrays."""
    dates = np.array([1, 2, 3, 4, 5], dtype=float)
    values = np.array([10, 12, 14, 16, 18], dtype=float)

    slope, intercept, r_squared, p_value = calculate_linear_trend(
        dates, values
    )

    assert slope > 0
    assert r_squared > 0.99


def test_linear_trend_with_lists():
    """Test linear trend works with plain Python lists."""
    dates = [1.0, 2.0, 3.0, 4.0, 5.0]
    values = [10, 12, 14, 16, 18]

    slope, intercept, r_squared, p_value = calculate_linear_trend(
        dates, values
    )

    assert slope > 0
    assert r_squared > 0.99


def test_linear_trend_with_nan_values():
    """Test linear trend handles NaN values by removing them."""
    dates = pd.date_range('2024-01-01', periods=6)
    values = [10, np.nan, 20, 30, np.nan, 40]

    slope, intercept, r_squared, p_value = calculate_linear_trend(
        dates, values
    )

    # Should work with valid data points (4 remaining)
    assert slope > 0
    assert np.isfinite(slope)


@pytest.mark.parametrize("dates,values,error_type,error_msg", [
    # Mismatched lengths
    (
        pd.date_range('2024-01-01', periods=5),
        [10, 20, 30],
        ValueError,
        "same length"
    ),
    # Too few points
    (
        pd.date_range('2024-01-01', periods=1),
        [10],
        ValueError,
        "At least 2"
    ),
    # All NaN values
    (
        pd.date_range('2024-01-01', periods=3),
        [np.nan, np.nan, np.nan],
        ValueError,
        "At least 2 valid"
    ),
])
def test_linear_trend_invalid_inputs(dates, values, error_type, error_msg):
    """Test linear trend raises appropriate errors for invalid inputs."""
    with pytest.raises(error_type, match=error_msg):
        calculate_linear_trend(dates, values)


# =============================================================================
# Tests for calculate_seasonal_average
# =============================================================================

@pytest.mark.parametrize("season,expected_months", [
    ('winter', [12, 1, 2]),
    ('spring', [3, 4, 5]),
    ('summer', [6, 7, 8]),
    ('fall', [9, 10, 11]),
    ('autumn', [9, 10, 11]),  # alias for fall
    ('WINTER', [12, 1, 2]),  # case insensitive
    ('Spring', [3, 4, 5]),  # mixed case
])
def test_seasonal_average_correct_months(season, expected_months):
    """Test seasonal average uses correct months for each season."""
    # Create data with known values for each month
    dates = pd.date_range('2024-01-01', periods=365)
    df = pd.DataFrame({
        'date': dates,
        'value': 0.0  # default value
    })

    # Set specific values for target months
    df['month'] = pd.to_datetime(df['date']).dt.month
    for month in expected_months:
        df.loc[df['month'] == month, 'value'] = 100.0

    avg = calculate_seasonal_average(df, season)

    # Should be close to 100 (the value we set for those months)
    assert abs(avg - 100.0) < 1.0


def test_seasonal_average_winter_handles_year_boundary():
    """Test winter season correctly handles Dec-Jan-Feb across year."""
    # Create two years of data
    dates = pd.date_range('2023-12-01', periods=90)
    df = pd.DataFrame({
        'date': dates,
        'value': 50.0
    })

    avg = calculate_seasonal_average(df, 'winter')
    assert abs(avg - 50.0) < 1.0


@pytest.mark.parametrize("season,values_by_month,expected_avg", [
    # Winter average
    ('winter', {12: 10, 1: 20, 2: 30}, 20.0),
    # Spring average
    ('spring', {3: 15, 4: 25, 5: 35}, 25.0),
])
def test_seasonal_average_calculations(season, values_by_month, expected_avg):
    """Test seasonal average calculates correct mean."""
    # Create data for full year
    dates = pd.date_range('2024-01-01', periods=365)
    df = pd.DataFrame({
        'date': dates,
        'value': 0.0
    })

    # Set specific values for target months
    df['month'] = pd.to_datetime(df['date']).dt.month
    for month, value in values_by_month.items():
        df.loc[df['month'] == month, 'value'] = value

    avg = calculate_seasonal_average(df, season)

    # Should match expected average
    assert abs(avg - expected_avg) < 1.0


@pytest.mark.parametrize("season,error_msg", [
    ('invalid_season', "Invalid season"),
    ('', "Invalid season"),
    ('winter2024', "Invalid season"),
])
def test_seasonal_average_invalid_season(season, error_msg):
    """Test seasonal average rejects invalid season names."""
    dates = pd.date_range('2024-01-01', periods=10)
    df = pd.DataFrame({
        'date': dates,
        'value': [10] * 10
    })

    with pytest.raises(ValueError, match=error_msg):
        calculate_seasonal_average(df, season)


def test_seasonal_average_missing_columns():
    """Test seasonal average raises error for missing columns."""
    df = pd.DataFrame({
        'wrong_column': [1, 2, 3]
    })

    with pytest.raises(KeyError, match="must contain 'date' and 'value'"):
        calculate_seasonal_average(df, 'winter')


def test_seasonal_average_no_data_for_season():
    """Test seasonal average handles case with no data for season."""
    # Only January data (winter month)
    dates = pd.date_range('2024-01-01', periods=31)
    df = pd.DataFrame({
        'date': dates,
        'value': [15.0] * 31
    })

    # Winter should work
    winter_avg = calculate_seasonal_average(df, 'winter')
    assert abs(winter_avg - 15.0) < 1.0

    # Summer should fail (no summer months)
    with pytest.raises(ValueError, match="No data found"):
        calculate_seasonal_average(df, 'summer')


# =============================================================================
# Tests for calculate_monthly_statistics
# =============================================================================

def test_monthly_statistics_structure():
    """Test monthly statistics returns correct DataFrame structure."""
    dates = pd.date_range('2024-01-01', periods=365)
    df = pd.DataFrame({
        'date': dates,
        'value': np.random.uniform(5, 25, 365)
    })

    result = calculate_monthly_statistics(df)

    # Check structure
    assert isinstance(result, pd.DataFrame)
    assert 'month' in result.columns
    assert 'mean' in result.columns
    assert 'median' in result.columns
    assert 'min' in result.columns
    assert 'max' in result.columns
    assert 'count' in result.columns

    # Should have 12 months
    assert len(result) == 12

    # Months should be 1-12
    assert set(result['month']) == set(range(1, 13))


def test_monthly_statistics_calculations():
    """Test monthly statistics calculates correct values."""
    # Create data with known monthly values
    dates = []
    values = []

    for month in range(1, 13):
        # 30 days per month with value = month * 10
        month_dates = pd.date_range(
            f'2024-{month:02d}-01',
            periods=min(30, 28 if month == 2 else 30)
        )
        dates.extend(month_dates)
        values.extend([month * 10] * len(month_dates))

    df = pd.DataFrame({
        'date': dates,
        'value': values
    })

    result = calculate_monthly_statistics(df)

    # Check January (month 1)
    jan = result[result['month'] == 1].iloc[0]
    assert abs(jan['mean'] - 10.0) < 0.01
    assert abs(jan['median'] - 10.0) < 0.01
    assert abs(jan['min'] - 10.0) < 0.01
    assert abs(jan['max'] - 10.0) < 0.01

    # Check December (month 12)
    dec = result[result['month'] == 12].iloc[0]
    assert abs(dec['mean'] - 120.0) < 0.01


def test_monthly_statistics_with_varying_data():
    """Test monthly statistics with realistic varying data."""
    dates = pd.date_range('2024-01-01', periods=90)
    values = [10, 15, 20] * 30  # Varying values

    df = pd.DataFrame({
        'date': dates,
        'value': values
    })

    result = calculate_monthly_statistics(df)

    # Check that min <= median <= max for each month
    for _, row in result.iterrows():
        assert row['min'] <= row['median'] <= row['max']
        assert row['min'] <= row['mean'] <= row['max']
        assert row['count'] > 0


def test_monthly_statistics_missing_columns():
    """Test monthly statistics raises error for missing columns."""
    df = pd.DataFrame({
        'wrong_column': [1, 2, 3]
    })

    with pytest.raises(KeyError, match="must contain 'date' and 'value'"):
        calculate_monthly_statistics(df)


def test_monthly_statistics_partial_year():
    """Test monthly statistics with partial year data."""
    # Only 3 months of data
    dates = pd.date_range('2024-01-01', periods=90)
    df = pd.DataFrame({
        'date': dates,
        'value': np.random.uniform(10, 20, 90)
    })

    result = calculate_monthly_statistics(df)

    # Should only have 3 months
    assert len(result) == 3
    assert set(result['month']) == {1, 2, 3}


def test_monthly_statistics_with_nan():
    """Test monthly statistics handles NaN values correctly."""
    dates = pd.date_range('2024-01-01', periods=31)
    values = [10] * 31
    values[10] = np.nan  # Add one NaN

    df = pd.DataFrame({
        'date': dates,
        'value': values
    })

    result = calculate_monthly_statistics(df)

    jan = result[result['month'] == 1].iloc[0]
    # Mean should still be 10 (NaN excluded by pandas)
    assert abs(jan['mean'] - 10.0) < 0.01
    # Count should be 30 (pandas count excludes NaN by default)
    assert jan['count'] == 30
