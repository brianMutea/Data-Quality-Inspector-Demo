"""Generate Markdown and HTML reports from quality check results."""

from datetime import datetime
from html import escape
from pathlib import Path

from dqi.console import console, print_success, print_info


def _build_summary_rows(null_results: dict, duplicate_results: dict, outlier_results: dict, type_results: dict) -> list[dict]:
    """Build top-level summary rows shared by markdown and html outputs."""
    if null_results["critical_indicators"]:
        null_status = "fail"
        null_detail = f"{len(null_results['critical_indicators'])} critical indicators"
    elif null_results["warning_indicators"]:
        null_status = "warn"
        null_detail = f"{len(null_results['warning_indicators'])} warning indicators"
    else:
        null_status = "pass"
        null_detail = f"{null_results['overall_null_pct']}% nulls overall"

    type_issues = (
        type_results["country_code_issues"]
        + type_results["indicator_code_issues"]
        + type_results["year_issues"]
        + type_results["value_issues"]
    )

    return [
        {"check": "Null Analysis", "status": null_status, "detail": null_detail},
        {
            "check": "Duplicates",
            "status": "pass" if duplicate_results["verdict"] == "pass" else "fail",
            "detail": f"{duplicate_results['duplicate_count']} duplicates ({duplicate_results['duplicate_pct']}%)",
        },
        {
            "check": "Outlier Analysis",
            "status": "pass",
            "detail": f"{outlier_results['total_outliers_found']} outliers found",
        },
        {
            "check": "Type Consistency",
            "status": "pass" if type_results["verdict"] == "pass" else "fail",
            "detail": f"{len(type_issues)} issues found" if type_issues else "All checks passed",
        },
    ]


def _status_icon(status: str) -> str:
    return {"pass": "OK", "warn": "WARN", "fail": "FAIL"}.get(status, "N/A")


def _save_bar_chart(title: str, x_values: list[str], y_values: list[float], y_label: str, output_file: Path) -> bool:
    """Save a basic bar chart to disk if plotting backend is available."""
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return False

    if not x_values:
        return False

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(x_values, y_values)
    ax.set_title(title)
    ax.set_ylabel(y_label)
    ax.set_xlabel("Indicator")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(output_file, dpi=150)
    plt.close(fig)
    return True


def _generate_chart_assets(null_results: dict, outlier_results: dict, summary_rows: list[dict], assets_dir: Path) -> dict[str, str]:
    """Generate all chart assets and return asset-name to relative-path map."""
    assets_dir.mkdir(parents=True, exist_ok=True)
    chart_links: dict[str, str] = {}

    sorted_nulls = sorted(
        null_results["per_indicator"].items(),
        key=lambda item: item[1]["null_pct"],
        reverse=True,
    )
    null_x = [item[0] for item in sorted_nulls]
    null_y = [item[1]["null_pct"] for item in sorted_nulls]
    null_chart = assets_dir / "null_percentage_by_indicator.png"
    if _save_bar_chart("Null Percentage by Indicator", null_x, null_y, "Null %", null_chart):
        chart_links["nulls"] = null_chart.name

    sorted_outliers = [
        item
        for item in sorted(
            outlier_results["per_indicator"].items(),
            key=lambda item: item[1]["outlier_count"],
            reverse=True,
        )
        if item[1]["status"] == "analysed"
    ]
    outlier_x = [item[0] for item in sorted_outliers]
    outlier_y = [item[1]["outlier_count"] for item in sorted_outliers]
    outlier_chart = assets_dir / "outlier_count_by_indicator.png"
    if _save_bar_chart("Outlier Count by Indicator", outlier_x, outlier_y, "Outlier count", outlier_chart):
        chart_links["outliers"] = outlier_chart.name

    severity_score = {"pass": 0, "warn": 1, "fail": 2}
    summary_x = [row["check"] for row in summary_rows]
    summary_y = [severity_score.get(row["status"], 0) for row in summary_rows]
    summary_chart = assets_dir / "summary_severity_by_check.png"
    if _save_bar_chart("Summary Severity by Check", summary_x, summary_y, "Severity score", summary_chart):
        chart_links["summary"] = summary_chart.name

    return chart_links


def _render_markdown(
    schema: dict,
    null_results: dict,
    duplicate_results: dict,
    outlier_results: dict,
    type_results: dict,
    summary_rows: list[dict],
    chart_links: dict[str, str],
) -> str:
    lines: list[str] = []
    lines.append("# Data Quality Report — World Bank Development Indicators")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- Generated: {datetime.now().isoformat()}")
    lines.append(f"- Total rows: {schema['row_count']}")
    lines.append(f"- Economies: {schema['economy_count']}")
    lines.append(f"- Indicators: {schema['indicator_count']}")
    lines.append(f"- Nulls overall: {null_results['overall_null_pct']}%")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Check | Status | Detail |")
    lines.append("|-------|--------|--------|")
    for row in summary_rows:
        lines.append(f"| {row['check']} | {_status_icon(row['status'])} | {row['detail']} |")
    lines.append("")

    if "summary" in chart_links:
        lines.append("![Summary severity by check](assets/" + chart_links["summary"] + ")")
        lines.append("")

    lines.append("## Metadata")
    lines.append("")
    lines.append("- Source: World Bank Open Data API (wbgapi)")
    lines.append(f"- Year range: {schema['year_range'][0]}-{schema['year_range'][1]}")
    for indicator in schema["indicators"]:
        lines.append(f"- Indicator: {indicator}")
    lines.append("")

    lines.append("## Null Analysis")
    lines.append("")
    lines.append(
        f"Overall null percentage: {null_results['overall_null_pct']}% "
        f"({null_results['overall_null_count']} of {null_results['total_rows']} rows)"
    )
    lines.append("")
    if "nulls" in chart_links:
        lines.append("![Null percentage by indicator](assets/" + chart_links["nulls"] + ")")
        lines.append("")
    lines.append("| Indicator | Total Rows | Null Count | Null % | Severity |")
    lines.append("|-----------|------------|------------|--------|----------|")
    sorted_nulls = sorted(null_results["per_indicator"].items(), key=lambda x: x[1]["null_pct"], reverse=True)
    for indicator_code, result in sorted_nulls:
        lines.append(
            f"| {indicator_code} | {result['total_rows']} | {result['null_count']} | "
            f"{result['null_pct']}% | {result['severity']} |"
        )
    lines.append("")

    lines.append("## Duplicate Analysis")
    lines.append("")
    lines.append(
        f"Duplicate count: {duplicate_results['duplicate_count']} "
        f"({duplicate_results['duplicate_pct']}% of {duplicate_results['total_rows']} rows)"
    )
    lines.append("")
    if duplicate_results["duplicate_count"] > 0:
        lines.append("| Country Code | Indicator Code | Year |")
        lines.append("|--------------|----------------|------|")
        for example in duplicate_results["examples"]:
            lines.append(f"| {example['country_code']} | {example['indicator_code']} | {example['year']} |")
    else:
        lines.append("No duplicate records detected.")
    lines.append("")

    lines.append("## Outlier Analysis")
    lines.append("")
    lines.append(f"Total outliers found: {outlier_results['total_outliers_found']} across all indicators")
    lines.append("")
    if "outliers" in chart_links:
        lines.append("![Outlier count by indicator](assets/" + chart_links["outliers"] + ")")
        lines.append("")
    lines.append("| Indicator | Outlier Count | Outlier % | Lower Bound | Upper Bound |")
    lines.append("|-----------|---------------|-----------|-------------|-------------|")
    sorted_outliers = sorted(outlier_results["per_indicator"].items(), key=lambda x: x[1]["outlier_count"], reverse=True)
    for indicator_code, result in sorted_outliers:
        if result["status"] == "analysed":
            lower = f"{result['lower_bound']:.2e}" if result["lower_bound"] is not None else "N/A"
            upper = f"{result['upper_bound']:.2e}" if result["upper_bound"] is not None else "N/A"
            lines.append(f"| {indicator_code} | {result['outlier_count']} | {result['outlier_pct']}% | {lower} | {upper} |")
    lines.append("")

    lines.append("## Type Consistency")
    lines.append("")
    type_issues = (
        type_results["country_code_issues"]
        + type_results["indicator_code_issues"]
        + type_results["year_issues"]
        + type_results["value_issues"]
    )
    if not type_issues:
        lines.append("All columns passed type consistency checks.")
    else:
        for key, header in [
            ("country_code_issues", "Country Code Issues"),
            ("indicator_code_issues", "Indicator Code Issues"),
            ("year_issues", "Year Issues"),
            ("value_issues", "Value Issues"),
        ]:
            if type_results[key]:
                lines.append(f"**{header}:**")
                for issue in type_results[key]:
                    lines.append(f"- {issue}")
                lines.append("")

    lines.append("---")
    lines.append("*Generated by DataQualityInspector using World Bank Open Data via wbgapi*")
    return "\n".join(lines)


def _render_html(
    schema: dict,
    null_results: dict,
    duplicate_results: dict,
    outlier_results: dict,
    type_results: dict,
    summary_rows: list[dict],
    chart_links: dict[str, str],
) -> str:
    summary_table_rows = "\n".join(
        [
            f"<tr><td>{escape(row['check'])}</td><td>{escape(_status_icon(row['status']))}</td><td>{escape(row['detail'])}</td></tr>"
            for row in summary_rows
        ]
    )
    null_rows = "\n".join(
        [
            (
                "<tr>"
                f"<td>{escape(indicator)}</td><td>{result['total_rows']}</td><td>{result['null_count']}</td>"
                f"<td>{result['null_pct']}%</td><td>{escape(result['severity'])}</td>"
                "</tr>"
            )
            for indicator, result in sorted(
                null_results["per_indicator"].items(),
                key=lambda x: x[1]["null_pct"],
                reverse=True,
            )
        ]
    )
    outlier_rows = "\n".join(
        [
            (
                "<tr>"
                f"<td>{escape(indicator)}</td><td>{result['outlier_count']}</td><td>{result['outlier_pct']}%</td>"
                f"<td>{(f'{result['lower_bound']:.2e}' if result['lower_bound'] is not None else 'N/A')}</td>"
                f"<td>{(f'{result['upper_bound']:.2e}' if result['upper_bound'] is not None else 'N/A')}</td>"
                "</tr>"
            )
            for indicator, result in sorted(
                outlier_results["per_indicator"].items(),
                key=lambda x: x[1]["outlier_count"],
                reverse=True,
            )
            if result["status"] == "analysed"
        ]
    )
    issues_html = ""
    for key, header in [
        ("country_code_issues", "Country Code Issues"),
        ("indicator_code_issues", "Indicator Code Issues"),
        ("year_issues", "Year Issues"),
        ("value_issues", "Value Issues"),
    ]:
        if type_results[key]:
            issues_html += f"<h4>{escape(header)}</h4><ul>"
            for issue in type_results[key]:
                issues_html += f"<li>{escape(issue)}</li>"
            issues_html += "</ul>"
    if not issues_html:
        issues_html = "<p>All columns passed type consistency checks.</p>"

    chart_summary = f'<img src="assets/{escape(chart_links["summary"])}" alt="Summary chart">' if "summary" in chart_links else ""
    chart_null = f'<img src="assets/{escape(chart_links["nulls"])}" alt="Null chart">' if "nulls" in chart_links else ""
    chart_outlier = f'<img src="assets/{escape(chart_links["outliers"])}" alt="Outlier chart">' if "outliers" in chart_links else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Data Quality Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; line-height: 1.4; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .card {{ border: 1px solid #ccc; border-radius: 8px; padding: 12px; margin-bottom: 16px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 8px 0 16px; }}
    th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; }}
    img {{ max-width: 100%; height: auto; margin: 8px 0 16px; }}
  </style>
</head>
<body>
  <h1>Data Quality Report - World Bank Development Indicators</h1>
  <div class="card">
    <h2>Executive Summary</h2>
    <p>Generated: {escape(datetime.now().isoformat())}</p>
    <p>Rows: {schema['row_count']} | Economies: {schema['economy_count']} | Indicators: {schema['indicator_count']}</p>
    <table>
      <thead><tr><th>Check</th><th>Status</th><th>Detail</th></tr></thead>
      <tbody>{summary_table_rows}</tbody>
    </table>
    {chart_summary}
  </div>
  <div class="card">
    <h2>Null Analysis</h2>
    <p>Overall null percentage: {null_results['overall_null_pct']}% ({null_results['overall_null_count']} of {null_results['total_rows']} rows)</p>
    {chart_null}
    <table>
      <thead><tr><th>Indicator</th><th>Total Rows</th><th>Null Count</th><th>Null %</th><th>Severity</th></tr></thead>
      <tbody>{null_rows}</tbody>
    </table>
  </div>
  <div class="card">
    <h2>Duplicate Analysis</h2>
    <p>Duplicate count: {duplicate_results['duplicate_count']} ({duplicate_results['duplicate_pct']}% of {duplicate_results['total_rows']} rows)</p>
  </div>
  <div class="card">
    <h2>Outlier Analysis</h2>
    <p>Total outliers found: {outlier_results['total_outliers_found']}</p>
    {chart_outlier}
    <table>
      <thead><tr><th>Indicator</th><th>Outlier Count</th><th>Outlier %</th><th>Lower Bound</th><th>Upper Bound</th></tr></thead>
      <tbody>{outlier_rows}</tbody>
    </table>
  </div>
  <div class="card">
    <h2>Type Consistency</h2>
    {issues_html}
  </div>
</body>
</html>
"""


def generate_report(
    schema: dict,
    null_results: dict,
    duplicate_results: dict,
    outlier_results: dict,
    type_results: dict,
    output_path: str,
    html_output_path: str | None = None,
    assets_dir: str = "reports/assets",
) -> None:
    """
    Generate markdown and optional html quality reports and chart assets.
    """
    markdown_path = Path(output_path)
    html_path = Path(html_output_path) if html_output_path else markdown_path.with_suffix(".html")
    assets_path = Path(assets_dir)

    console.print(f"[blue]ℹ[/blue] Writing reports to [cyan]{markdown_path.parent}[/cyan]...")

    summary_rows = _build_summary_rows(null_results, duplicate_results, outlier_results, type_results)
    chart_links = _generate_chart_assets(null_results, outlier_results, summary_rows, assets_path)

    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_content = _render_markdown(
        schema, null_results, duplicate_results, outlier_results, type_results, summary_rows, chart_links
    )
    markdown_path.write_text(markdown_content, encoding="utf-8")
    print_success(f"Markdown report saved: {markdown_path}")

    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_content = _render_html(
        schema, null_results, duplicate_results, outlier_results, type_results, summary_rows, chart_links
    )
    html_path.write_text(html_content, encoding="utf-8")
    print_success(f"HTML report saved: {html_path}")

    if chart_links:
        print_info(f"Chart assets saved to: {assets_path}")
