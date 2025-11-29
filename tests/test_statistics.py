"""Tests for the statistics module."""

import pytest
import numpy as np
from air_quality.statistics import (
    calculate_daily_mean,
    calculate_rolling_average,
    calculate_exceedance_count,
    calculate_aqi
)


# Tests for calculate_daily_mean
@pytest.mark.parametrize("values,expected", [
    ([10, 20, 30, 40, 50], 30.0),
    ([5.5, 10.5, 15.5], 10.5),
    ([1, 2, 3, 4, 5], 3.0),
    ([42], 42.0),
])
def test_calculate_daily_mean(values, expected):
    observed = calculate_daily_mean(values)
    assert abs(observed - expected) < 1e-10


def test_calculate_daily_mean_with_nan():
    values = [10, 20, np.nan, 30, 40]
    observed = calculate_daily_mean(values)
    expected = 25.0
    assert observed == expected


def test_calculate_daily_mean_empty():
    with pytest.raises(ValueError):
        calculate_daily_mean([])


def test_calculate_daily_mean_all_nan():
    with pytest.raises(ValueError):
        calculate_daily_mean([np.nan, np.nan])


# Tests for calculate_rolling_average
def test_calculate_rolling_average_basic():
    values = [1, 2, 3, 4, 5]
    observed = calculate_rolling_average(values, window=3)
    assert np.isnan(observed[0])
    assert np.isnan(observed[1])
    assert observed[2] == 2.0
    assert observed[3] == 3.0
    assert observed[4] == 4.0


def test_calculate_rolling_average_window_7():
    values = list(range(1, 11))
    observed = calculate_rolling_average(values, window=7)
    assert np.all(np.isnan(observed[:6]))
    assert observed[6] == 4.0
    assert observed[7] == 5.0


def test_calculate_rolling_average_window_one():
    values = [1, 2, 3, 4, 5]
    observed = calculate_rolling_average(values, window=1)
    np.testing.assert_array_equal(observed, values)


def test_calculate_rolling_average_invalid_window():
    with pytest.raises(ValueError):
        calculate_rolling_average([1, 2, 3], window=0)


# Tests for calculate_exceedance_count
@pytest.mark.parametrize("values,threshold,expected", [
    ([10, 20, 30, 40, 50], 25, 3),
    ([10, 20, 30], 50, 0),
    ([10, 20, 30, 40], 5, 4),
    ([10, 20, 30, 40], 30, 1),
    ([12.5, 35.4, 55.5, 150.5], 35.4, 2),
    ([], 10, 0),
])
def test_calculate_exceedance_count(values, threshold, expected):
    observed = calculate_exceedance_count(values, threshold)
    assert observed == expected


def test_calculate_exceedance_count_with_nan():
    values = [10, 20, np.nan, 30, 40, np.nan]
    observed = calculate_exceedance_count(values, threshold=15)
    expected = 3
    assert observed == expected


def test_calculate_exceedance_count_epa_standard():
    values = [20, 30, 35, 40, 50, 60]
    observed = calculate_exceedance_count(values, threshold=35.0)
    expected = 3
    assert observed == expected


# Tests for calculate_aqi (meaningful function)
@pytest.mark.parametrize("pm25,expected_category", [
    (10.0, "Good"),
    (25.0, "Moderate"),
    (45.0, "Unhealthy for Sensitive Groups"),
    (100.0, "Unhealthy"),
    (200.0, "Very Unhealthy"),
    (300.0, "Hazardous"),
])
def test_calculate_aqi_categories(pm25, expected_category):
    observed = calculate_aqi(pm25)
    assert observed['category'] == expected_category


def test_calculate_aqi_boundary_good():
    observed = calculate_aqi(12.0)
    assert observed['category'] == 'Good'
    assert observed['aqi'] == 50


def test_calculate_aqi_boundary_moderate():
    observed = calculate_aqi(35.4)
    assert observed['category'] == 'Moderate'
    assert observed['aqi'] == 100


def test_calculate_aqi_zero():
    observed = calculate_aqi(0.0)
    assert observed['category'] == 'Good'
    assert observed['aqi'] == 0


def test_calculate_aqi_extreme():
    observed = calculate_aqi(600.0)
    assert observed['category'] == 'Hazardous'
    assert observed['aqi'] == 500


def test_calculate_aqi_negative():
    with pytest.raises(ValueError):
        calculate_aqi(-10.0)


def test_calculate_aqi_nan():
    with pytest.raises(ValueError):
        calculate_aqi(np.nan)


def test_calculate_aqi_structure():
    observed = calculate_aqi(50.0)
    assert 'aqi' in observed
    assert 'category' in observed
    assert 'color' in observed
    assert 'health_message' in observed


def test_calculate_aqi_phoenix_event():
    observed = calculate_aqi(79.04)
    assert observed['category'] == 'Unhealthy'
    assert 151 <= observed['aqi'] <= 200


@pytest.mark.parametrize("pm25,expected_color", [
    (10.0, '#00E400'),
    (25.0, '#FFFF00'),
    (45.0, '#FF7E00'),
    (100.0, '#FF0000'),
    (200.0, '#8F3F97'),
    (300.0, '#7E0023'),
])
def test_calculate_aqi_colors(pm25, expected_color):
    observed = calculate_aqi(pm25)
    assert observed['color'] == expected_color
