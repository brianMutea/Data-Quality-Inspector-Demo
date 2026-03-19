"""Fetches World Bank Development Indicators using wbgapi."""

import pandas as pd
import wbgapi as wb

INDICATORS = [
    'NY.GDP.MKTP.CD',
    'SP.POP.TOTL',
    'SE.ADT.LITR.ZS',
    'SH.DYN.MORT',
    'EG.ELC.ACCS.ZS',
    'IT.NET.USER.ZS',
    'SL.UEM.TOTL.ZS',
    'SP.DYN.LE00.IN',
    'AG.LND.ARBL.ZS',
    'EN.ATM.CO2E.PC',
]

START_YEAR = 2000
END_YEAR = 2023


def fetch_data() -> tuple[pd.DataFrame, dict]:
    """
    Fetch World Bank Development Indicators and reshape into long format.
    
    Returns:
        tuple: (DataFrame with columns country_code, indicator_code, year, value,
                schema dict with metadata about the fetched data)
    """
    print("Fetching World Bank data for 10 indicators (2000-2023)...")
    
    try:
        raw = wb.data.DataFrame(
            INDICATORS,
            economy='all',
            time=range(START_YEAR, END_YEAR + 1),
            columns='series',
            numericTimeKeys=True
        )
    except Exception as e:
        print(f"Error: Failed to fetch data from World Bank API: {e}")
        print("Please check your internet connection and try again.")
        raise SystemExit(1)
    
    # Flatten MultiIndex to columns
    df_long = raw.reset_index()
    
    # Rename columns
    df_long = df_long.rename(columns={'economy': 'country_code', 'time': 'year'})
    
    # Melt indicator columns into long format
    df_melted = df_long.melt(
        id_vars=['country_code', 'year'],
        var_name='indicator_code',
        value_name='value'
    )
    
    # Ensure correct dtypes
    df_melted['year'] = df_melted['year'].astype(int)
    df_melted['value'] = df_melted['value'].astype(float)
    
    # Defensive cleanup
    df_melted = df_melted.dropna(subset=['country_code', 'indicator_code'], how='all')
    
    # Sort
    df_melted = df_melted.sort_values(['country_code', 'indicator_code', 'year']).reset_index(drop=True)
    
    # Build schema
    row_count = len(df_melted)
    indicator_count = df_melted['indicator_code'].nunique()
    economy_count = df_melted['country_code'].nunique()
    null_count = df_melted['value'].isna().sum()
    null_pct = round((null_count / row_count * 100) if row_count > 0 else 0.0, 2)
    
    print(f"Fetched {row_count} rows across {indicator_count} indicators and {economy_count} economies.")
    
    schema = {
        'row_count': row_count,
        'indicator_count': indicator_count,
        'economy_count': economy_count,
        'year_range': [START_YEAR, END_YEAR],
        'indicators': INDICATORS,
        'columns': list(df_melted.columns),
        'null_count': null_count,
        'null_pct': null_pct
    }
    
    return df_melted, schema
