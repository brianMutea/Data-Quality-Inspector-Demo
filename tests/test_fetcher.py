"""Tests for the fetcher module."""

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock


def test_fetch_data_returns_tuple():
    """Test that fetch_data returns a tuple of DataFrame and dict."""
    from dqi.fetcher import fetch_data, INDICATORS
    
    # Create mock raw data matching wbgapi structure
    mock_raw = pd.DataFrame(
        {
            'NY.GDP.MKTP.CD': [1e12, 2e12, 3e12],
            'SP.POP.TOTL': [1e8, 2e8, 3e8],
            'SE.ADT.LITR.ZS': [90.0, 85.0, 95.0],
            'SH.DYN.MORT': [10.0, 15.0, 20.0],
            'EG.ELC.ACCS.ZS': [80.0, 85.0, 90.0],
            'IT.NET.USER.ZS': [50.0, 60.0, 70.0],
            'SL.UEM.TOTL.ZS': [5.0, 6.0, 7.0],
            'SP.DYN.LE00.IN': [70.0, 72.0, 74.0],
            'AG.LND.ARBL.ZS': [30.0, 32.0, 34.0],
            'EN.ATM.CO2E.PC': [5.0, 6.0, 7.0],
        },
        index=pd.MultiIndex.from_tuples(
            [('USA', 2000), ('GBR', 2000), ('KEN', 2000)],
            names=['economy', 'time']
        )
    )
    
    with patch('wbgapi.data.DataFrame', return_value=mock_raw):
        df, schema = fetch_data(refresh_cache=True)
        
        # Check return types
        assert isinstance(df, pd.DataFrame)
        assert isinstance(schema, dict)
        
        # Check DataFrame columns
        assert set(df.columns) == {"country_code", "indicator_code", "year", "value"}
        
        # Check dtypes
        assert df['year'].dtype == int
        assert df['value'].dtype == float
        
        # Check schema keys
        required_keys = ['row_count', 'indicator_count', 'economy_count', 'year_range',
                        'indicators', 'columns', 'null_count', 'null_pct']
        for key in required_keys:
            assert key in schema
        
        # Check schema values
        assert schema['indicator_count'] == 10
        assert schema['indicators'] == INDICATORS
        assert set(schema['columns']) == {"country_code", "indicator_code", "year", "value"}
