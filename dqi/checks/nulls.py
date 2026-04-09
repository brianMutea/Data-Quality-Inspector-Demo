"""Null analysis check for data quality."""

import pandas as pd
from dqi.config import NULL_CRITICAL_THRESHOLD, NULL_WARNING_THRESHOLD
from dqi.utils import timed


@timed
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
    
    grouped = df.groupby('indicator_code', sort=False)['value']
    indicator_stats = grouped.agg(total_rows='size', null_count=lambda s: s.isna().sum())
    indicator_stats['null_pct'] = ((indicator_stats['null_count'] / indicator_stats['total_rows']) * 100).round(2)
    indicator_stats['severity'] = 'ok'
    indicator_stats.loc[indicator_stats['null_pct'] >= NULL_WARNING_THRESHOLD, 'severity'] = 'warning'
    indicator_stats.loc[indicator_stats['null_pct'] > NULL_CRITICAL_THRESHOLD, 'severity'] = 'critical'

    critical_indicators = indicator_stats.index[indicator_stats['severity'] == 'critical'].tolist()
    warning_indicators = indicator_stats.index[indicator_stats['severity'] == 'warning'].tolist()

    per_indicator = {
        indicator_code: {
            'null_count': int(row['null_count']),
            'null_pct': float(row['null_pct']),
            'total_rows': int(row['total_rows']),
            'severity': row['severity']
        }
        for indicator_code, row in indicator_stats.iterrows()
    }
    
    return {
        'overall_null_count': overall_null_count,
        'overall_null_pct': overall_null_pct,
        'total_rows': total_rows,
        'critical_indicators': critical_indicators,
        'warning_indicators': warning_indicators,
        'per_indicator': per_indicator
    }
