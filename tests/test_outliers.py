"""Tests for the outlier detection check."""

import pandas as pd
import numpy as np
from dqi.checks.outliers import check_outliers


def test_check_outliers_detects_extreme_outlier(sample_df):
    """Test that the extreme GDP outlier in sample_df is detected."""
    result = check_outliers(sample_df)
    
    assert 'NY.GDP.MKTP.CD' in result['per_indicator']
    gdp_result = result['per_indicator']['NY.GDP.MKTP.CD']
    assert gdp_result['outlier_count'] > 0


def test_check_outliers_returns_required_keys(sample_df):
    """Test that check_outliers returns all required keys."""
    result = check_outliers(sample_df)
    
    required_keys = ['total_outliers_found', 'indicators_with_outliers',
                     'skipped_indicators', 'per_indicator']
    for key in required_keys:
        assert key in result


def test_check_outliers_skips_insufficient_data():
    """Test that an indicator with fewer than 30 non-null values is skipped."""
    df = pd.DataFrame({
        'country_code': ['USA'] * 20,
        'indicator_code': ['TEST.INDICATOR'] * 20,
        'year': list(range(2000, 2020)),
        'value': [1.0] * 20
    })
    
    result = check_outliers(df)
    
    assert 'TEST.INDICATOR' in result['skipped_indicators']
    assert result['per_indicator']['TEST.INDICATOR']['status'] == 'skipped: insufficient data'
