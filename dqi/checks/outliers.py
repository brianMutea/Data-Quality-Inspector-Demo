"""Outlier detection check using IQR method."""

import pandas as pd


def check_outliers(df: pd.DataFrame) -> dict:
    """
    Detect outliers in the value column using IQR method, grouped by indicator.
    
    Args:
        df: DataFrame with columns country_code, indicator_code, year, value
        
    Returns:
        dict: Outlier analysis results with per-indicator statistics
    """
    print("Running outlier check...")
    
    per_indicator = {}
    total_outliers_found = 0
    indicators_with_outliers = []
    skipped_indicators = []
    
    unique_indicators = df['indicator_code'].unique()
    total_indicators = len(unique_indicators)
    
    for idx, indicator_code in enumerate(unique_indicators, 1):
        print(f"Outlier check: {idx}/{total_indicators} indicators processed...")
        
        indicator_df = df[df['indicator_code'] == indicator_code]
        values = indicator_df['value'].dropna()
        
        if len(values) < 30:
            per_indicator[indicator_code] = {
                'outlier_count': 0,
                'outlier_pct': 0.0,
                'lower_bound': None,
                'upper_bound': None,
                'sample_outliers': [],
                'status': 'skipped: insufficient data'
            }
            skipped_indicators.append(indicator_code)
            continue
        
        # IQR calculation
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Find outliers
        outlier_mask = (values < lower_bound) | (values > upper_bound)
        outlier_count = outlier_mask.sum()
        outlier_pct = round((outlier_count / len(values) * 100) if len(values) > 0 else 0.0, 2)
        
        # Sample outliers
        sample_outliers = values[outlier_mask].head(5).tolist()
        
        per_indicator[indicator_code] = {
            'outlier_count': outlier_count,
            'outlier_pct': outlier_pct,
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'sample_outliers': sample_outliers,
            'status': 'analysed'
        }
        
        total_outliers_found += outlier_count
        if outlier_count > 0:
            indicators_with_outliers.append(indicator_code)
    
    return {
        'total_outliers_found': total_outliers_found,
        'indicators_with_outliers': indicators_with_outliers,
        'skipped_indicators': skipped_indicators,
        'per_indicator': per_indicator
    }
