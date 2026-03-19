"""Tests for the report generator."""

import pytest
from dqi.reporter import generate_report


def test_generate_report_creates_file(tmp_path):
    """Test that generate_report creates a file at the specified path."""
    output_path = tmp_path / "test_report.md"
    
    # Minimal valid result dicts
    schema = {
        'row_count': 100,
        'indicator_count': 10,
        'economy_count': 5,
        'year_range': [2000, 2023],
        'indicators': ['NY.GDP.MKTP.CD', 'SP.POP.TOTL'],
        'columns': ['country_code', 'indicator_code', 'year', 'value'],
        'null_count': 10,
        'null_pct': 10.0
    }
    
    null_results = {
        'overall_null_count': 10,
        'overall_null_pct': 10.0,
        'total_rows': 100,
        'critical_indicators': [],
        'warning_indicators': [],
        'per_indicator': {
            'NY.GDP.MKTP.CD': {'null_count': 5, 'null_pct': 5.0, 'total_rows': 50, 'severity': 'ok'}
        }
    }
    
    duplicate_results = {
        'duplicate_count': 0,
        'duplicate_pct': 0.0,
        'total_rows': 100,
        'examples': [],
        'verdict': 'pass'
    }
    
    outlier_results = {
        'total_outliers_found': 2,
        'indicators_with_outliers': ['NY.GDP.MKTP.CD'],
        'skipped_indicators': [],
        'per_indicator': {
            'NY.GDP.MKTP.CD': {
                'outlier_count': 2,
                'outlier_pct': 4.0,
                'lower_bound': 1e12,
                'upper_bound': 2e13,
                'sample_outliers': [9.99e13],
                'status': 'analysed'
            }
        }
    }
    
    type_results = {
        'country_code_issues': [],
        'indicator_code_issues': [],
        'year_issues': [],
        'value_issues': [],
        'verdict': 'pass'
    }
    
    generate_report(schema, null_results, duplicate_results, outlier_results, type_results, str(output_path))
    
    assert output_path.exists()


def test_generate_report_contains_required_headings(tmp_path):
    """Test that the output file contains all required section headings."""
    output_path = tmp_path / "test_report.md"
    
    # Minimal valid result dicts (same as above)
    schema = {
        'row_count': 100,
        'indicator_count': 10,
        'economy_count': 5,
        'year_range': [2000, 2023],
        'indicators': ['NY.GDP.MKTP.CD'],
        'columns': ['country_code', 'indicator_code', 'year', 'value'],
        'null_count': 10,
        'null_pct': 10.0
    }
    
    null_results = {
        'overall_null_count': 10,
        'overall_null_pct': 10.0,
        'total_rows': 100,
        'critical_indicators': [],
        'warning_indicators': [],
        'per_indicator': {
            'NY.GDP.MKTP.CD': {'null_count': 10, 'null_pct': 10.0, 'total_rows': 100, 'severity': 'ok'}
        }
    }
    
    duplicate_results = {
        'duplicate_count': 0,
        'duplicate_pct': 0.0,
        'total_rows': 100,
        'examples': [],
        'verdict': 'pass'
    }
    
    outlier_results = {
        'total_outliers_found': 0,
        'indicators_with_outliers': [],
        'skipped_indicators': [],
        'per_indicator': {
            'NY.GDP.MKTP.CD': {
                'outlier_count': 0,
                'outlier_pct': 0.0,
                'lower_bound': 1e12,
                'upper_bound': 2e13,
                'sample_outliers': [],
                'status': 'analysed'
            }
        }
    }
    
    type_results = {
        'country_code_issues': [],
        'indicator_code_issues': [],
        'year_issues': [],
        'value_issues': [],
        'verdict': 'pass'
    }
    
    generate_report(schema, null_results, duplicate_results, outlier_results, type_results, str(output_path))
    
    content = output_path.read_text()
    
    assert "# Data Quality Report" in content
    assert "## Summary" in content
    assert "## Null Analysis" in content
    assert "## Duplicate Analysis" in content
    assert "## Outlier Analysis" in content
    assert "## Type Consistency" in content
