"""Tests for the report generator."""

import importlib.util

from dqi.reporter import generate_report


def _sample_payloads() -> tuple[dict, dict, dict, dict, dict]:
    schema = {
        "row_count": 100,
        "indicator_count": 2,
        "economy_count": 5,
        "year_range": [2000, 2023],
        "indicators": ["NY.GDP.MKTP.CD", "SP.POP.TOTL"],
        "columns": ["country_code", "indicator_code", "year", "value"],
        "null_count": 10,
        "null_pct": 10.0,
    }
    null_results = {
        "overall_null_count": 10,
        "overall_null_pct": 10.0,
        "total_rows": 100,
        "critical_indicators": [],
        "warning_indicators": ["SP.POP.TOTL"],
        "per_indicator": {
            "NY.GDP.MKTP.CD": {"null_count": 5, "null_pct": 5.0, "total_rows": 50, "severity": "ok"},
            "SP.POP.TOTL": {"null_count": 5, "null_pct": 15.0, "total_rows": 50, "severity": "warning"},
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
        "total_outliers_found": 2,
        "indicators_with_outliers": ["NY.GDP.MKTP.CD"],
        "skipped_indicators": [],
        "per_indicator": {
            "NY.GDP.MKTP.CD": {
                "outlier_count": 2,
                "outlier_pct": 4.0,
                "lower_bound": 1e12,
                "upper_bound": 2e13,
                "sample_outliers": [9.99e13],
                "status": "analysed",
            },
            "SP.POP.TOTL": {
                "outlier_count": 0,
                "outlier_pct": 0.0,
                "lower_bound": 1e4,
                "upper_bound": 1e8,
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
    return schema, null_results, duplicate_results, outlier_results, type_results


def test_generate_report_creates_markdown_html_and_assets(tmp_path):
    markdown_path = tmp_path / "quality_report.md"
    html_path = tmp_path / "quality_report.html"
    assets_path = tmp_path / "assets"
    schema, null_results, duplicate_results, outlier_results, type_results = _sample_payloads()

    generate_report(
        schema,
        null_results,
        duplicate_results,
        outlier_results,
        type_results,
        str(markdown_path),
        str(html_path),
        str(assets_path),
    )

    assert markdown_path.exists()
    assert html_path.exists()
    assert assets_path.exists()
    has_matplotlib = importlib.util.find_spec("matplotlib") is not None
    if has_matplotlib:
        assert any(assets_path.glob("*.png"))


def test_generate_report_contains_required_headings(tmp_path):
    markdown_path = tmp_path / "quality_report.md"
    html_path = tmp_path / "quality_report.html"
    assets_path = tmp_path / "assets"
    schema, null_results, duplicate_results, outlier_results, type_results = _sample_payloads()
    generate_report(
        schema,
        null_results,
        duplicate_results,
        outlier_results,
        type_results,
        str(markdown_path),
        str(html_path),
        str(assets_path),
    )

    content = markdown_path.read_text()
    assert "# Data Quality Report" in content
    assert "## Executive Summary" in content
    assert "## Summary" in content
    assert "## Null Analysis" in content
    assert "## Duplicate Analysis" in content
    assert "## Outlier Analysis" in content
    assert "## Type Consistency" in content
