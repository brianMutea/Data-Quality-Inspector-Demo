"""Pytest fixtures for DataQualityInspector tests."""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_df():
    """
    Create a sample DataFrame matching the long format from fetcher.py.
    
    Returns:
        pd.DataFrame: Sample data with deliberate quality issues for testing
    """
    indicators = ['NY.GDP.MKTP.CD', 'SP.POP.TOTL', 'SE.ADT.LITR.ZS', 'SH.DYN.MORT', 'EN.ATM.CO2E.PC']
    countries = ['USA', 'GBR', 'KEN', 'BRA', 'IND']
    years = list(range(2000, 2020))
    
    rows = []
    for country in countries:
        for indicator in indicators:
            for year in years:
                rows.append({
                    'country_code': country,
                    'indicator_code': indicator,
                    'year': year,
                    'value': np.nan  # Will be filled below
                })
    
    df = pd.DataFrame(rows)
    
    # Fill with realistic values
    np.random.seed(42)
    for idx, row in df.iterrows():
        if row['indicator_code'] == 'NY.GDP.MKTP.CD':
            # GDP values
            df.at[idx, 'value'] = np.random.uniform(1e12, 2.5e13)
        elif row['indicator_code'] == 'SP.POP.TOTL':
            # Population values
            df.at[idx, 'value'] = np.random.uniform(5e7, 3e8)
        elif row['indicator_code'] == 'SE.ADT.LITR.ZS':
            # Literacy rate
            df.at[idx, 'value'] = np.random.uniform(60, 99)
        elif row['indicator_code'] == 'SH.DYN.MORT':
            # Mortality rate
            df.at[idx, 'value'] = np.random.uniform(5, 50)
        elif row['indicator_code'] == 'EN.ATM.CO2E.PC':
            # CO2 emissions
            df.at[idx, 'value'] = np.random.uniform(1, 15)
    
    # Add deliberate nulls (30% of rows)
    null_indices = np.random.choice(df.index, size=int(len(df) * 0.3), replace=False)
    df.loc[null_indices, 'value'] = np.nan
    
    # Add one extreme outlier in GDP
    gdp_mask = df['indicator_code'] == 'NY.GDP.MKTP.CD'
    outlier_idx = df[gdp_mask].index[0]
    df.at[outlier_idx, 'value'] = 9.99e13
    
    # Add one duplicate row
    duplicate_row = df.iloc[0].copy()
    df = pd.concat([df, pd.DataFrame([duplicate_row])], ignore_index=True)
    
    # Ensure correct dtypes
    df['year'] = df['year'].astype(int)
    df['value'] = df['value'].astype(float)
    
    return df
