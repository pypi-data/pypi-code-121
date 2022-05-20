import pytest

from calorine.data_analysis import (analyze_data,
                                    get_autocorrelation_function,
                                    get_correlation_length,
                                    get_error_estimate,
                                    _estimate_correlation_length_from_acf,
                                    _estimate_error)
import numpy as np


@pytest.fixture
def data():
    """Simplified but representative data series."""
    return np.arange(1000) % 20


@pytest.fixture
def data_flat():
    """Data series without variation."""
    return np.zeros(20)


@pytest.fixture
def target_values():
    """Target values for reasonable data series."""
    return {'correlation_length': 4,
            'error_estimate': 0.7156495464548879,
            'mean': 9.5,
            'std': 5.766281297335398}


@pytest.fixture
def target_values_flat():
    """Target values for data series without any variation."""
    return {'correlation_length': np.nan,
            'error_estimate': np.nan,
            'mean': 0,
            'std': 0}


def test_analyze_data(data, target_values):
    """Tests the analyze_data function."""
    res = analyze_data(data)
    assert isinstance(res, dict)
    assert len(res) == len(target_values)
    for key, val in target_values.items():
        assert key in res
        assert abs(res[key] - val) < 1e-6


def test_analyze_data_flat(data_flat, target_values_flat):
    """Tests the analyze_data function."""
    res = analyze_data(data_flat)
    assert isinstance(res, dict)
    assert len(res) == len(target_values_flat)
    for key, val in target_values_flat.items():
        assert key in res
        if np.isnan(val):
            assert np.isnan(res[key])
        else:
            assert abs(res[key] - val) < 1e-6


def test_get_autocorrelation_function(data):
    """Tests the calculation of autocorrelation function."""
    autocorr = get_autocorrelation_function(data)
    assert isinstance(autocorr, np.ndarray)
    assert len(autocorr) == len(data) - 1
    assert abs(max(autocorr) - 1) < 1e-6
    assert abs(min(autocorr) - -0.5037974683544306) < 1e-6
    for i in range(len(autocorr) // 20):
        assert abs(autocorr[20 * i] - 1) < 1e-6


def test_get_autocorrelation_function_flat(data_flat):
    """Tests the calculation of autocorrelation function with a flat dataset."""
    autocorr = get_autocorrelation_function(data_flat)
    assert isinstance(autocorr, np.ndarray)
    assert len(autocorr) == len(data_flat) - 1
    for i in autocorr:
        assert np.isnan(i)


def test_get_autocorrelation_function_max_lag(data):
    """Tests the calculation of autocorrelation function with max_lag specified."""
    max_lag = 40
    autocorr = get_autocorrelation_function(data, max_lag=max_lag)
    assert isinstance(autocorr, np.ndarray)
    assert len(autocorr) == max_lag
    for i in range(len(autocorr) // 20):
        assert abs(autocorr[20 * i] - 1) < 1e-6


def test_get_autocorrelation_function_bad_max_lag(data):
    """Tests the calculation of autocorrelation function with too long max_lag."""
    max_lag = len(data) + 1
    with pytest.raises(ValueError) as e:
        get_autocorrelation_function(data, max_lag=max_lag)
    assert 'max_lag should be between 1 and len(data)-1' in str(e)


def test_get_correlation_length(data, target_values):
    """Tests calculation of correlation length."""
    corr_length = get_correlation_length(data)
    assert abs(corr_length - target_values['correlation_length']) < 1e-6


def test_get_correlation_length_flat(data_flat):
    """Tests calculation of correlation length with flat data series."""
    corr_length = get_correlation_length(data_flat)
    assert corr_length is None


def test_get_error_estimate(data, target_values):
    """Tests get_error_estimate function."""
    error = get_error_estimate(data)
    assert abs(error - target_values['error_estimate']) < 1e-6


def test_get_error_estimate_flat(data_flat):
    """Tests get_error_estimate function with flat data series."""
    error = get_error_estimate(data_flat)
    assert error is None


def test_estimate_correlation_length_from_acf():
    """Tests calculation of correlation length estimate from autocorrelation function."""
    acf = [1, 0.5, 0.01, -0.01, 1]
    corr_length = _estimate_correlation_length_from_acf(acf)
    assert corr_length == 2


def test_estimate_correlation_length_from_acf_flat_data():
    """
    Tests calculation of correlation length estimate from autocorrelation function
    with a flat data series.
    """
    acf = [1, 1, 1, 1, 1]
    corr_length = _estimate_correlation_length_from_acf(acf)
    assert corr_length is None


def test_estimate_error(data, target_values):
    """Tests error estimate function"""
    error = _estimate_error(data, correlation_length=4, confidence=0.95)
    assert np.abs(error - target_values['error_estimate']) < 1e-6
