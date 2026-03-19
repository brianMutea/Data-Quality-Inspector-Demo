"""Type consistency check for data quality."""

import pandas as pd
import re


def check_types(df: pd.DataFrame) -> dict:
    """
    Check type consistency and format validity for all columns.
    
    Args:
        df: DataFrame with columns country_code, indicator_code, year, value
        
    Returns:
        dict: Type consistency results with issues per column and verdict
    """
    print("Running type consistency check...")
    
    country_code_issues = []
    indicator_code_issues = []
    year_issues = []
    value_issues = []
    
    # Check country_code
    if df['country_code'].isna().any():
        null_count = df['country_code'].isna().sum()
        country_code_issues.append(f"{null_count} null values found")
    
    empty_country = df['country_code'].apply(lambda x: isinstance(x, str) and len(x) == 0)
    if empty_country.any():
        country_code_issues.append(f"{empty_country.sum()} empty strings found")
    
    invalid_length = df['country_code'].apply(
        lambda x: isinstance(x, str) and len(x) not in [2, 3]
    )
    if invalid_length.any():
        count = invalid_length.sum()
        country_code_issues.append(f"{count} values with invalid length (not 2 or 3 characters)")
    
    # Check indicator_code
    if df['indicator_code'].isna().any():
        null_count = df['indicator_code'].isna().sum()
        indicator_code_issues.append(f"{null_count} null values found")
    
    empty_indicator = df['indicator_code'].apply(lambda x: isinstance(x, str) and len(x) == 0)
    if empty_indicator.any():
        indicator_code_issues.append(f"{empty_indicator.sum()} empty strings found")
    
    # Pattern: dot-separated uppercase alphanumeric segments
    indicator_pattern = re.compile(r'^[A-Z0-9]+(\.[A-Z0-9]+)+$')
    invalid_pattern = df['indicator_code'].apply(
        lambda x: isinstance(x, str) and not indicator_pattern.match(x)
    )
    if invalid_pattern.any():
        count = invalid_pattern.sum()
        indicator_code_issues.append(f"{count} values with invalid format")
    
    # Check year
    if not pd.api.types.is_integer_dtype(df['year']):
        year_issues.append("Year column is not integer dtype")
    
    out_of_range = (df['year'] < 2000) | (df['year'] > 2023)
    if out_of_range.any():
        count = out_of_range.sum()
        year_issues.append(f"{count} values outside range 2000-2023")
    
    # Check value
    non_null_values = df['value'].dropna()
    if len(non_null_values) > 0:
        non_numeric = non_null_values.apply(lambda x: not isinstance(x, (int, float)))
        if non_numeric.any():
            count = non_numeric.sum()
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
