"""Tests for shared audit summary row building."""

from dqi.summary import build_summary_rows


def test_build_summary_rows_keys_and_critical_null_maps_to_fail_cli():
    null_results = {
        "critical_indicators": ["X.Y.Z"],
        "warning_indicators": [],
        "overall_null_pct": 12.5,
        "overall_null_count": 1,
        "total_rows": 10,
        "per_indicator": {},
    }
    dup = {"duplicate_count": 1, "duplicate_pct": 1.0, "total_rows": 100, "examples": [], "verdict": "fail"}
    outlier = {"total_outliers_found": 3, "indicators_with_outliers": [], "skipped_indicators": [], "per_indicator": {}}
    types = {"country_code_issues": [], "indicator_code_issues": [], "year_issues": [], "value_issues": [], "verdict": "pass"}

    rows = build_summary_rows(null_results, dup, outlier, types)

    assert len(rows) == 4
    assert rows[0]["check"] == "Null Analysis"
    assert rows[0]["status"] == "fail"
    assert rows[0]["cli_status"] == "critical"
    assert rows[3]["check"] == "Type Consistency"
    assert rows[3]["cli_status"] == "pass"


def test_outlier_row_cli_analysed_when_outliers_positive():
    null_results = {
        "critical_indicators": [],
        "warning_indicators": [],
        "overall_null_pct": 0,
        "overall_null_count": 0,
        "total_rows": 10,
        "per_indicator": {},
    }
    dup = {"duplicate_count": 0, "duplicate_pct": 0.0, "total_rows": 10, "examples": [], "verdict": "pass"}
    outlier = {"total_outliers_found": 1, "indicators_with_outliers": [], "skipped_indicators": [], "per_indicator": {}}
    types = {"country_code_issues": [], "indicator_code_issues": [], "year_issues": [], "value_issues": [], "verdict": "pass"}

    rows = build_summary_rows(null_results, dup, outlier, types)
    assert rows[2]["cli_status"] == "analysed"


def test_outlier_row_cli_pass_when_zero():
    null_results = {
        "critical_indicators": [],
        "warning_indicators": [],
        "overall_null_pct": 0,
        "overall_null_count": 0,
        "total_rows": 10,
        "per_indicator": {},
    }
    dup = {"duplicate_count": 0, "duplicate_pct": 0.0, "total_rows": 10, "examples": [], "verdict": "pass"}
    outlier = {"total_outliers_found": 0, "indicators_with_outliers": [], "skipped_indicators": [], "per_indicator": {}}
    types = {"country_code_issues": [], "indicator_code_issues": [], "year_issues": [], "value_issues": [], "verdict": "pass"}

    rows = build_summary_rows(null_results, dup, outlier, types)
    assert rows[2]["cli_status"] == "pass"

