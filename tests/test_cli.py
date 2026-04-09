"""Tests for the CLI argument parsing and report dispatch."""

from unittest.mock import MagicMock, patch

from dqi.cli import build_parser, main


def test_build_parser_includes_html_and_assets_options():
    """Parser exposes --html-output and --assets-dir with expected defaults."""
    parser = build_parser()
    args = parser.parse_args([])

    assert hasattr(args, "html_output")
    assert hasattr(args, "assets_dir")
    assert args.html_output is None
    assert args.assets_dir == "reports/assets"


@patch("dqi.cli.generate_report")
@patch("dqi.cli.check_types")
@patch("dqi.cli.check_outliers")
@patch("dqi.cli.check_duplicates")
@patch("dqi.cli.check_nulls")
@patch("dqi.cli.fetch_data")
def test_main_passes_html_and_assets_to_reporter(
    mock_fetch_data: MagicMock,
    mock_check_nulls: MagicMock,
    mock_check_duplicates: MagicMock,
    mock_check_outliers: MagicMock,
    mock_check_types: MagicMock,
    mock_generate_report: MagicMock,
):
    """CLI main forwards output options to generate_report."""
    mock_fetch_data.return_value = (
        MagicMock(),
        {
            "row_count": 1,
            "indicator_count": 1,
            "economy_count": 1,
            "year_range": [2000, 2023],
            "indicators": ["NY.GDP.MKTP.CD"],
            "columns": ["country_code", "indicator_code", "year", "value"],
            "null_count": 0,
            "null_pct": 0.0,
        },
    )
    mock_check_nulls.return_value = {
        "overall_null_count": 0,
        "overall_null_pct": 0.0,
        "total_rows": 1,
        "critical_indicators": [],
        "warning_indicators": [],
        "per_indicator": {
            "NY.GDP.MKTP.CD": {"null_count": 0, "null_pct": 0.0, "total_rows": 1, "severity": "ok"}
        },
    }
    mock_check_duplicates.return_value = {
        "duplicate_count": 0,
        "duplicate_pct": 0.0,
        "total_rows": 1,
        "examples": [],
        "verdict": "pass",
    }
    mock_check_outliers.return_value = {
        "total_outliers_found": 0,
        "indicators_with_outliers": [],
        "skipped_indicators": [],
        "per_indicator": {
            "NY.GDP.MKTP.CD": {
                "outlier_count": 0,
                "outlier_pct": 0.0,
                "lower_bound": 0.0,
                "upper_bound": 1.0,
                "sample_outliers": [],
                "status": "analysed",
            }
        },
    }
    mock_check_types.return_value = {
        "country_code_issues": [],
        "indicator_code_issues": [],
        "year_issues": [],
        "value_issues": [],
        "verdict": "pass",
    }

    main(
        [
            "--output",
            "reports/quality_report.md",
            "--html-output",
            "reports/quality_report.html",
            "--assets-dir",
            "reports/assets",
        ]
    )

    _, kwargs = mock_generate_report.call_args
    assert kwargs["html_output_path"] == "reports/quality_report.html"
    assert kwargs["assets_dir"] == "reports/assets"
