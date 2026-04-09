"""Tests for CLI argument wiring and orchestration."""

from unittest.mock import Mock

import dqi.cli as cli


def _check_payload() -> dict:
    return {"verdict": "pass", "duplicate_count": 0, "duplicate_pct": 0.0, "total_rows": 1, "examples": []}


def test_main_uses_default_report_paths(monkeypatch):
    mock_fetch = Mock(return_value=(object(), {"row_count": 1, "economy_count": 1, "indicator_count": 1}))
    mock_nulls = Mock(return_value={"overall_null_count": 0, "overall_null_pct": 0.0, "total_rows": 1, "critical_indicators": [], "warning_indicators": [], "per_indicator": {}})
    mock_dups = Mock(return_value=_check_payload())
    mock_outliers = Mock(return_value={"total_outliers_found": 0, "skipped_indicators": [], "per_indicator": {}})
    mock_types = Mock(return_value={"country_code_issues": [], "indicator_code_issues": [], "year_issues": [], "value_issues": [], "verdict": "pass"})
    mock_report = Mock()

    monkeypatch.setattr(cli, "fetch_data", mock_fetch)
    monkeypatch.setattr(cli, "check_nulls", mock_nulls)
    monkeypatch.setattr(cli, "check_duplicates", mock_dups)
    monkeypatch.setattr(cli, "check_outliers", mock_outliers)
    monkeypatch.setattr(cli, "check_types", mock_types)
    monkeypatch.setattr(cli, "generate_report", mock_report)
    monkeypatch.setattr("sys.argv", ["prog"])

    cli.main()

    mock_fetch.assert_called_once_with(refresh_cache=False)
    mock_report.assert_called_once()
    report_call = mock_report.call_args[0]
    assert report_call[5] == "reports/quality_report.md"
    assert report_call[6] == "reports/quality_report.html"
    assert report_call[7] == "reports/assets"


def test_main_passes_custom_paths_and_refresh(monkeypatch):
    mock_fetch = Mock(return_value=(object(), {"row_count": 1, "economy_count": 1, "indicator_count": 1}))
    mock_nulls = Mock(return_value={"overall_null_count": 0, "overall_null_pct": 0.0, "total_rows": 1, "critical_indicators": [], "warning_indicators": [], "per_indicator": {}})
    mock_dups = Mock(return_value=_check_payload())
    mock_outliers = Mock(return_value={"total_outliers_found": 0, "skipped_indicators": [], "per_indicator": {}})
    mock_types = Mock(return_value={"country_code_issues": [], "indicator_code_issues": [], "year_issues": [], "value_issues": [], "verdict": "pass"})
    mock_report = Mock()

    monkeypatch.setattr(cli, "fetch_data", mock_fetch)
    monkeypatch.setattr(cli, "check_nulls", mock_nulls)
    monkeypatch.setattr(cli, "check_duplicates", mock_dups)
    monkeypatch.setattr(cli, "check_outliers", mock_outliers)
    monkeypatch.setattr(cli, "check_types", mock_types)
    monkeypatch.setattr(cli, "generate_report", mock_report)
    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--refresh",
            "--output",
            "tmp/custom.md",
            "--html-output",
            "tmp/custom.html",
            "--assets-dir",
            "tmp/assets",
        ],
    )

    cli.main()

    mock_fetch.assert_called_once_with(refresh_cache=True)
    report_call = mock_report.call_args[0]
    assert report_call[5] == "tmp/custom.md"
    assert report_call[6] == "tmp/custom.html"
    assert report_call[7] == "tmp/assets"
