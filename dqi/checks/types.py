"""Type consistency check for data quality."""

import pandas as pd
from dqi.config import YEAR_MIN, YEAR_MAX, COUNTRY_CODE_VALID_LENGTHS, INDICATOR_CODE_PATTERN
from dqi.utils import timed


@timed
def check_types(df: pd.DataFrame) -> dict:
    """
    Check type consistency and format validity for all columns.

    Args:
        df: DataFrame with columns country_code, indicator_code, year, value

    Returns:
        dict: Type consistency results with issues per column and verdict
    """
    country_code_issues = []
    indicator_code_issues = []
    year_issues = []
    value_issues = []
    
    # Check country_code
    if df['country_code'].isna().any():
        null_count = df['country_code'].isna().sum()
        country_code_issues.append(f"{null_count} null values found")
    
    country_code_str = df['country_code'].astype('string')

    empty_country = country_code_str.str.len().eq(0).fillna(False)
    if empty_country.any():
        country_code_issues.append(f"{empty_country.sum()} empty strings found")

    invalid_length = country_code_str.str.len().isin(COUNTRY_CODE_VALID_LENGTHS).eq(False) & country_code_str.notna()
    if invalid_length.any():
        count = invalid_length.sum()
        lengths_str = ' or '.join(str(l) for l in COUNTRY_CODE_VALID_LENGTHS)
        country_code_issues.append(f"{count} values with invalid length (not {lengths_str} characters)")
    
    # Check indicator_code
    if df['indicator_code'].isna().any():
        null_count = df['indicator_code'].isna().sum()
        indicator_code_issues.append(f"{null_count} null values found")
    
    indicator_code_str = df['indicator_code'].astype('string')

    empty_indicator = indicator_code_str.str.len().eq(0).fillna(False)
    if empty_indicator.any():
        indicator_code_issues.append(f"{empty_indicator.sum()} empty strings found")

    # Pattern: dot-separated uppercase alphanumeric segments
    invalid_pattern = indicator_code_str.str.fullmatch(INDICATOR_CODE_PATTERN).eq(False) & indicator_code_str.notna()
    if invalid_pattern.any():
        count = invalid_pattern.sum()
        indicator_code_issues.append(f"{count} values with invalid format")
    
    # Check year
    if not pd.api.types.is_integer_dtype(df['year']):
        year_issues.append("Year column is not integer dtype")
    
    # World Bank API returns integer years on [YEAR_MIN, YEAR_MAX] inclusive.
    out_of_range = (df['year'] < YEAR_MIN) | (df['year'] > YEAR_MAX)
    if out_of_range.any():
        count = out_of_range.sum()
        year_issues.append(f"{count} values outside range {YEAR_MIN}-{YEAR_MAX}")
    
    # Check value
    non_null_values = df['value'].dropna()
    if len(non_null_values) > 0:
        non_numeric = pd.to_numeric(non_null_values, errors='coerce').isna()
        if non_numeric.any():
            count = int(non_numeric.sum())
            value_issues.append(f"{count} non-numeric values found")
    
    # Determine verdict
    all_issues = country_code_issues + indicator_code_issues + year_issues + value_issues
    verdict = 'pass' if len(all_issues) == 0 else 'warn'
    
    return {
        'country_code_issues': country_code_issues,
        'indicator_code_issues': indicator_code_issues,
        'year_issues': year_issues,
        'value_issues': value_issues,
        'verdict': verdict
    }
