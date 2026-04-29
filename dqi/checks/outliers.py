"""Outlier detection check using IQR method."""

import pandas as pd
from dqi.config import OUTLIER_MIN_DATA_POINTS, OUTLIER_IQR_MULTIPLIER, OUTLIER_SAMPLE_SIZE, OUTLIER_Q1_PERCENTILE, OUTLIER_Q3_PERCENTILE
from dqi.utils import timed


@timed
def check_outliers(df: pd.DataFrame) -> dict:
    """
    Detect outliers in the value column using IQR method, grouped by indicator.

    Args:
        df: DataFrame with columns country_code, indicator_code, year, value

    Returns:
        dict: Outlier analysis results with per-indicator statistics
    """
    # Compute per-indicator IQR statistics in one vectorized pass
    grouped = df.groupby('indicator_code')['value']
    value_counts = grouped.count()
    q1 = grouped.quantile(OUTLIER_Q1_PERCENTILE)
    q3 = grouped.quantile(OUTLIER_Q3_PERCENTILE)
    iqr = q3 - q1
    lower_bounds = q1 - OUTLIER_IQR_MULTIPLIER * iqr
    upper_bounds = q3 + OUTLIER_IQR_MULTIPLIER * iqr

    # Join per-indicator bounds back onto every row — one lookup, not N full-table scans
    stats = pd.DataFrame({
        'lower_bound': lower_bounds,
        'upper_bound': upper_bounds,
        'count': value_counts,
    })
    df_aug = df.join(stats, on='indicator_code')

    # Single vectorized outlier mask across the entire DataFrame
    sufficient = df_aug['count'] > OUTLIER_MIN_DATA_POINTS
    outlier_mask = (
        sufficient
        & df_aug['value'].notna()
        & ((df_aug['value'] < df_aug['lower_bound']) | (df_aug['value'] > df_aug['upper_bound']))
    )

    # Per-indicator counts and samples derived from the mask via groupby
    outlier_counts = df_aug[outlier_mask].groupby('indicator_code')['value'].count()
    sample_outliers_map = (
        df_aug[outlier_mask]
        .groupby('indicator_code')['value']
        .apply(lambda x: x.head(OUTLIER_SAMPLE_SIZE).tolist())
    )

    # Assemble output dict — no DataFrame filtering inside this loop
    per_indicator = {}
    total_outliers_found = 0
    indicators_with_outliers = []
    skipped_indicators = []

    for indicator_code in df['indicator_code'].unique():
        count = value_counts.get(indicator_code, 0)

        if count < OUTLIER_MIN_DATA_POINTS:
            per_indicator[indicator_code] = {
                'outlier_count': 0,
                'outlier_pct': 0.0,
                'lower_bound': None,
                'upper_bound': None,
                'sample_outliers': [],
                'status': 'skipped: insufficient data',
            }
            skipped_indicators.append(indicator_code)
            continue

        outlier_count = int(outlier_counts.get(indicator_code, 0))
        outlier_pct = round(outlier_count / count * 100, 2)

        per_indicator[indicator_code] = {
            'outlier_count': outlier_count,
            'outlier_pct': outlier_pct,
            'lower_bound': float(lower_bounds[indicator_code]),
            'upper_bound': float(upper_bounds[indicator_code]),
            'sample_outliers': sample_outliers_map.get(indicator_code, []),
            'status': 'analysed',
        }

        total_outliers_found += outlier_count
        if outlier_count > 0:
            indicators_with_outliers.append(indicator_code)

    return {
        'total_outliers_found': total_outliers_found,
        'indicators_with_outliers': indicators_with_outliers,
        'skipped_indicators': skipped_indicators,
        'per_indicator': per_indicator,
    }
