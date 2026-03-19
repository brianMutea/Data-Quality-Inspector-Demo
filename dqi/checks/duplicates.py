"""Duplicate detection check for data quality."""

import pandas as pd


def check_duplicates(df: pd.DataFrame) -> dict:
    """
    Detect duplicate rows based on country_code + indicator_code + year combination.
    
    Args:
        df: DataFrame with columns country_code, indicator_code, year, value
        
    Returns:
        dict: Duplicate analysis results with count, percentage, and examples
    """
    print("Running duplicate check...")
    
    total_rows = len(df)
    
    # Find duplicates based on the combination
    duplicate_mask = df.duplicated(subset=['country_code', 'indicator_code', 'year'], keep='first')
    duplicate_count = duplicate_mask.sum()
    duplicate_pct = round((duplicate_count / total_rows * 100) if total_rows > 0 else 0.0, 2)
    
    # Get examples
    examples = []
    if duplicate_count > 0:
        duplicate_rows = df[duplicate_mask].head(5)
        for _, row in duplicate_rows.iterrows():
            examples.append({
                'country_code': row['country_code'],
                'indicator_code': row['indicator_code'],
                'year': row['year']
            })
    
    verdict = 'pass' if duplicate_count == 0 else 'fail'
    
    return {
        'duplicate_count': duplicate_count,
        'duplicate_pct': duplicate_pct,
        'total_rows': total_rows,
        'examples': examples,
        'verdict': verdict
    }
