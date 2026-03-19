"""Null analysis check for data quality."""

import pandas as pd


def check_nulls(df: pd.DataFrame) -> dict:
    """
    Analyze null values in the value column grouped by indicator.
    
    Args:
        df: DataFrame with columns country_code, indicator_code, year, value
        
    Returns:
        dict: Null analysis results with overall and per-indicator statistics
    """
    print("Running null check...")
    
    total_rows = len(df)
    overall_null_count = df['value'].isna().sum()
    overall_null_pct = round((overall_null_count / total_rows * 100) if total_rows > 0 else 0.0, 2)
    
    per_indicator = {}
    critical_indicators = []
    warning_indicators = []
    
    for indicator_code in df['indicator_code'].unique():
        indicator_df = df[df['indicator_code'] == indicator_code]
        indicator_total = len(indicator_df)
        indicator_nulls = indicator_df['value'].isna().sum()
        indicator_null_pct = round((indicator_nulls / indicator_total * 100) if indicator_total > 0 else 0.0, 2)
        
        if indicator_null_pct > 50:
            severity = 'critical'
            critical_indicators.append(indicator_code)
        elif indicator_null_pct >= 20:
            severity = 'warning'
            warning_indicators.append(indicator_code)
        else:
            severity = 'ok'
        
        per_indicator[indicator_code] = {
            'null_count': indicator_nulls,
            'null_pct': indicator_null_pct,
            'total_rows': indicator_total,
            'severity': severity
        }
    
    return {
        'overall_null_count': overall_null_count,
        'overall_null_pct': overall_null_pct,
        'total_rows': total_rows,
        'critical_indicators': critical_indicators,
        'warning_indicators': warning_indicators,
        'per_indicator': per_indicator
    }
