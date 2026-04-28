"""Shared audit summary rows used by the CLI and Markdown/HTML reports."""

from __future__ import annotations


def build_summary_rows(
    null_results: dict,
    duplicate_results: dict,
    outlier_results: dict,
    type_results: dict,
) -> list[dict]:
    """
    Build top-level summary rows shared by Markdown, HTML, and the Rich CLI table.

    Each row dict has:
        check: Display name for the audit.
        status: Canonical status for Markdown (pass | warn | fail).
        detail: Human-readable explanation.
        cli_status: Status token for Rich styling (defaults to cli_status_fallback(status)).
    """
    if null_results["critical_indicators"]:
        null_status = "fail"
        null_detail = f"{len(null_results['critical_indicators'])} critical indicators"
        null_cli = "critical"
    elif null_results["warning_indicators"]:
        null_status = "warn"
        null_detail = f"{len(null_results['warning_indicators'])} warning indicators"
        null_cli = "warn"
    else:
        null_status = "pass"
        null_detail = f"{null_results['overall_null_pct']}% nulls overall"
        null_cli = "pass"

    type_issues = (
        type_results["country_code_issues"]
        + type_results["indicator_code_issues"]
        + type_results["year_issues"]
        + type_results["value_issues"]
    )

    dup_status = "pass" if duplicate_results["verdict"] == "pass" else "fail"

    total_outliers = outlier_results["total_outliers_found"]
    outlier_status = "pass"
    outlier_detail = f"{total_outliers} outliers found"
    outlier_cli = "analysed" if total_outliers > 0 else "pass"

    type_status = "pass" if type_results["verdict"] == "pass" else "fail"
    type_detail = f"{len(type_issues)} issues found" if type_issues else "All checks passed"

    return [
        {"check": "Null Analysis", "status": null_status, "detail": null_detail, "cli_status": null_cli},
        {
            "check": "Duplicates",
            "status": dup_status,
            "detail": f"{duplicate_results['duplicate_count']} duplicates ({duplicate_results['duplicate_pct']}%)",
            "cli_status": dup_status,
        },
        {
            "check": "Outlier Analysis",
            "status": outlier_status,
            "detail": outlier_detail,
            "cli_status": outlier_cli,
        },
        {
            "check": "Type Consistency",
            "status": type_status,
            "detail": type_detail,
            "cli_status": type_status,
        },
    ]
