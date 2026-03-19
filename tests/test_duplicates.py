"""Tests for the duplicate detection check."""

import pandas as pd
from dqi.checks.duplicates import check_duplicates


def test_check_duplicates_detects_duplicate(sample_df):
    """Test that check_duplicates detects the duplicate row in sample_df."""
    result = check_duplicates(sample_df)
    
    assert result['duplicate_count'] == 1
    assert result['verdict'] == 'fail'


def test_check_duplicates_no_duplicates():
    """Test that a duplicate-free DataFrame returns verdict 'pass'."""
    df = pd.DataFrame({
        'country_code': ['USA', 'GBR', 'KEN'],
        'indicator_code': ['NY.GDP.MKTP.CD', 'NY.GDP.MKTP.CD', 'NY.GDP.MKTP.CD'],
        'year': [2000, 2000, 2000],
        'value': [1e12, 2e12, 3e12]
    })
    
    result = check_duplicates(df)
    
    assert result['duplicate_count'] == 0
    assert result['verdict'] == 'pass'
