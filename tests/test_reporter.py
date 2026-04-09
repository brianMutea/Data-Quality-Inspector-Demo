"""Tests for the report generator."""

from dqi.reporter import generate_report


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


def test_generate_report_writes_html_and_assets(tmp_path):
    """Generating HTML output also writes chart assets in the requested directory."""
    markdown_path = tmp_path / "report.md"
    html_path = tmp_path / "report.html"
    assets_dir = tmp_path / "reports" / "assets"

    schema = {
        "row_count": 100,
        "indicator_count": 2,
        "economy_count": 5,
        "year_range": [2000, 2023],
        "indicators": ["NY.GDP.MKTP.CD", "SP.POP.TOTL"],
        "columns": ["country_code", "indicator_code", "year", "value"],
        "null_count": 20,
        "null_pct": 20.0,
    }
    null_results = {
        "overall_null_count": 20,
        "overall_null_pct": 20.0,
        "total_rows": 100,
        "critical_indicators": [],
        "warning_indicators": ["SP.POP.TOTL"],
        "per_indicator": {
            "NY.GDP.MKTP.CD": {"null_count": 5, "null_pct": 10.0, "total_rows": 50, "severity": "ok"},
            "SP.POP.TOTL": {"null_count": 15, "null_pct": 30.0, "total_rows": 50, "severity": "warning"},
        },
    }
    duplicate_results = {
        "duplicate_count": 0,
        "duplicate_pct": 0.0,
        "total_rows": 100,
        "examples": [],
        "verdict": "pass",
    }
    outlier_results = {
        "total_outliers_found": 3,
        "indicators_with_outliers": ["NY.GDP.MKTP.CD"],
        "skipped_indicators": [],
        "per_indicator": {
            "NY.GDP.MKTP.CD": {
                "outlier_count": 3,
                "outlier_pct": 6.0,
                "lower_bound": 1.0,
                "upper_bound": 10.0,
                "sample_outliers": [11.0],
                "status": "analysed",
            },
            "SP.POP.TOTL": {
                "outlier_count": 0,
                "outlier_pct": 0.0,
                "lower_bound": 1.0,
                "upper_bound": 10.0,
                "sample_outliers": [],
                "status": "analysed",
            },
        },
    }
    type_results = {
        "country_code_issues": [],
        "indicator_code_issues": [],
        "year_issues": [],
        "value_issues": [],
        "verdict": "pass",
    }

    generate_report(
        schema,
        null_results,
        duplicate_results,
        outlier_results,
        type_results,
        str(markdown_path),
        html_output_path=str(html_path),
        assets_dir=str(assets_dir),
    )

    assert markdown_path.exists()
    assert html_path.exists()
    assert (assets_dir / "null_percentage_by_indicator.png").exists()
    assert (assets_dir / "outlier_count_by_indicator.png").exists()
