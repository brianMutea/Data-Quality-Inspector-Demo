"""Tests for the null analysis check."""

import pandas as pd
import numpy as np
from dqi.checks.nulls import check_nulls


def test_check_nulls_returns_required_keys(sample_df):
    """Test that check_nulls returns all required keys."""
    result = check_nulls(sample_df)
    
    required_keys = ['overall_null_count', 'overall_null_pct', 'total_rows',
                     'critical_indicators', 'warning_indicators', 'per_indicator']
    for key in required_keys:
        assert key in result


def test_check_nulls_counts_match(sample_df):
    """Test that overall_null_count matches actual nulls in sample_df."""
    result = check_nulls(sample_df)
    
    actual_null_count = sample_df['value'].isna().sum()
    assert result['overall_null_count'] == actual_null_count


def test_check_nulls_severity_critical():
    """Test that an indicator with 60% nulls gets severity 'critical'."""
    df = pd.DataFrame({
        'country_code': ['USA'] * 10,
        'indicator_code': ['TEST.INDICATOR'] * 10,
        'year': list(range(2000, 2010)),
        'value': [1.0, 2.0, 3.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    })
    
    result = check_nulls(df)
    
    assert 'TEST.INDICATOR' in result['per_indicator']
    assert result['per_indicator']['TEST.INDICATOR']['severity'] == 'critical'
    assert 'TEST.INDICATOR' in result['critical_indicators']
