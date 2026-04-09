"""Generate Markdown and HTML reports from quality check results."""

from datetime import datetime
from html import escape
from pathlib import Path
import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def _ensure_parent_dir(path_str: str) -> Path:
    """Create parent directories for a file path and return Path object."""
    path = Path(path_str)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _build_summary_rows(null_results: dict, duplicate_results: dict, outlier_results: dict, type_results: dict) -> list[dict]:
    """Return normalized summary rows for both Markdown and HTML rendering."""
    if null_results["critical_indicators"]:
        null_status = "fail"
        null_detail = f"{len(null_results['critical_indicators'])} critical indicators"
    elif null_results["warning_indicators"]:
        null_status = "fail"
        null_detail = f"{len(null_results['warning_indicators'])} warning indicators"
    else:
        null_status = "pass"
        null_detail = f"{null_results['overall_null_pct']}% nulls overall"

    duplicates_status = "pass" if duplicate_results["verdict"] == "pass" else "fail"
    duplicates_detail = (
        f"{duplicate_results['duplicate_count']} duplicates "
        f"({duplicate_results['duplicate_pct']}%)"
    )

    outlier_status = "pass"
    outlier_detail = f"{outlier_results['total_outliers_found']} outliers found"

    all_type_issues = (
        type_results["country_code_issues"]
        + type_results["indicator_code_issues"]
        + type_results["year_issues"]
        + type_results["value_issues"]
    )
    type_status = "pass" if type_results["verdict"] == "pass" else "fail"
    type_detail = f"{len(all_type_issues)} issues found" if all_type_issues else "All checks passed"

    return [
        {"check": "Null Analysis", "status": null_status, "detail": null_detail},
        {"check": "Duplicates", "status": duplicates_status, "detail": duplicates_detail},
        {"check": "Outlier Analysis", "status": outlier_status, "detail": outlier_detail},
        {"check": "Type Consistency", "status": type_status, "detail": type_detail},
    ]


def _status_mark(status: str) -> str:
    """Convert normalized status value to visible pass/fail mark."""
    return "PASS" if status == "pass" else "FAIL"


def _relative_asset_path(from_file: Path, asset_file: Path) -> str:
    """Build a portable relative path from a report file to an asset file."""
    rel = os.path.relpath(str(asset_file), start=str(from_file.parent))
    return rel.replace("\\", "/")


def _generate_chart_assets(null_results: dict, outlier_results: dict, assets_dir: str) -> dict[str, Path]:
    """Generate visualization assets and return their resolved file paths."""
    assets_path = Path(assets_dir)
    assets_path.mkdir(parents=True, exist_ok=True)

    generated_assets: dict[str, Path] = {}

    null_sorted = sorted(
        null_results["per_indicator"].items(),
        key=lambda item: item[1]["null_pct"],
        reverse=True,
    )
    if null_sorted:
        labels = [item[0] for item in null_sorted]
        values = [item[1]["null_pct"] for item in null_sorted]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(labels, values, color="#4e79a7")
        ax.set_title("Null Percentage by Indicator")
        ax.set_ylabel("Null %")
        ax.set_xlabel("Indicator")
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        fig.tight_layout()
        null_chart_path = assets_path / "null_percentage_by_indicator.png"
        fig.savefig(null_chart_path, dpi=120)
        plt.close(fig)
        generated_assets["null_pct_chart"] = null_chart_path

    outlier_sorted = sorted(
        outlier_results["per_indicator"].items(),
        key=lambda item: item[1]["outlier_count"],
        reverse=True,
    )
    if outlier_sorted:
        labels = [item[0] for item in outlier_sorted]
        values = [item[1]["outlier_count"] for item in outlier_sorted]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(labels, values, color="#f28e2b")
        ax.set_title("Outlier Count by Indicator")
        ax.set_ylabel("Outlier Count")
        ax.set_xlabel("Indicator")
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        fig.tight_layout()
        outlier_chart_path = assets_path / "outlier_count_by_indicator.png"
        fig.savefig(outlier_chart_path, dpi=120)
        plt.close(fig)
        generated_assets["outlier_count_chart"] = outlier_chart_path

    return generated_assets


def _build_markdown_report(
    schema: dict,
    null_results: dict,
    duplicate_results: dict,
    outlier_results: dict,
    type_results: dict,
    markdown_path: Path,
    generated_assets: dict[str, Path],
) -> str:
    """Build report content in Markdown format."""
    lines: list[str] = []

    lines.append("# Data Quality Report - World Bank Development Indicators")
    lines.append("")
    lines.append("**Metadata:**")
    lines.append("")
    lines.append("- Source: World Bank Open Data API (wbgapi)")
    lines.append(f"- Indicators: {schema['indicator_count']}")
    for indicator in schema["indicators"]:
        lines.append(f"  - {indicator}")
    lines.append(f"- Year range: {schema['year_range'][0]}-{schema['year_range'][1]}")
    lines.append(f"- Economies: {schema['economy_count']} countries and regions")
    lines.append(f"- Total rows: {schema['row_count']}")
    lines.append(f"- Generated: {datetime.now().isoformat()}")
    lines.append("")

    summary_rows = _build_summary_rows(null_results, duplicate_results, outlier_results, type_results)
    lines.append("## Summary")
    lines.append("")
    lines.append("| Check | Status | Detail |")
    lines.append("|-------|--------|--------|")
    for row in summary_rows:
        lines.append(f"| {row['check']} | {_status_mark(row['status'])} | {row['detail']} |")
    lines.append("")

    lines.append("## Null Analysis")
    lines.append("")
    lines.append(
        f"Overall null percentage: {null_results['overall_null_pct']}% "
        f"({null_results['overall_null_count']} of {null_results['total_rows']} rows)"
    )
    lines.append("")
    lines.append("| Indicator | Total Rows | Null Count | Null % | Severity |")
    lines.append("|-----------|------------|------------|--------|----------|")
    sorted_nulls = sorted(
        null_results["per_indicator"].items(),
        key=lambda item: item[1]["null_pct"],
        reverse=True,
    )
    for indicator_code, result in sorted_nulls:
        lines.append(
            f"| {indicator_code} | {result['total_rows']} | {result['null_count']} | "
            f"{result['null_pct']}% | {result['severity']} |"
        )
    lines.append("")
    lines.append(
        f"{len(null_results['critical_indicators'])} critical and "
        f"{len(null_results['warning_indicators'])} warning indicators identified."
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
        lines.append("**Examples:**")
        lines.append("")
        lines.append("| Country Code | Indicator Code | Year |")
        lines.append("|--------------|----------------|------|")
        for example in duplicate_results["examples"]:
            lines.append(
                f"| {example['country_code']} | {example['indicator_code']} | {example['year']} |"
            )
        lines.append("")
    else:
        lines.append("No duplicate records detected.")
        lines.append("")

    lines.append("## Outlier Analysis")
    lines.append("")
    lines.append(
        f"Total outliers found: {outlier_results['total_outliers_found']} "
        "across all indicators"
    )
    lines.append("")
    lines.append("| Indicator | Outlier Count | Outlier % | Lower Bound | Upper Bound |")
    lines.append("|-----------|---------------|-----------|-------------|-------------|")
    sorted_outliers = sorted(
        outlier_results["per_indicator"].items(),
        key=lambda item: item[1]["outlier_count"],
        reverse=True,
    )
    for indicator_code, result in sorted_outliers:
        if result["status"] == "analysed":
            lower = f"{result['lower_bound']:.2e}" if result["lower_bound"] is not None else "N/A"
            upper = f"{result['upper_bound']:.2e}" if result["upper_bound"] is not None else "N/A"
            lines.append(
                f"| {indicator_code} | {result['outlier_count']} | {result['outlier_pct']}% | "
                f"{lower} | {upper} |"
            )
    lines.append("")
    if outlier_results["skipped_indicators"]:
        lines.append(
            f"**Note:** {len(outlier_results['skipped_indicators'])} indicators skipped due "
            "to insufficient data (< 30 non-null values): "
            + ", ".join(outlier_results["skipped_indicators"])
        )
        lines.append("")

    if generated_assets:
        lines.append("## Visualizations")
        lines.append("")
        if "null_pct_chart" in generated_assets:
            rel_path = _relative_asset_path(markdown_path, generated_assets["null_pct_chart"])
            lines.append("### Null Percentage by Indicator")
            lines.append(f"![Null Percentage by Indicator]({rel_path})")
            lines.append("")
        if "outlier_count_chart" in generated_assets:
            rel_path = _relative_asset_path(markdown_path, generated_assets["outlier_count_chart"])
            lines.append("### Outlier Count by Indicator")
            lines.append(f"![Outlier Count by Indicator]({rel_path})")
            lines.append("")

    lines.append("## Type Consistency")
    lines.append("")
    all_type_issues = (
        type_results["country_code_issues"]
        + type_results["indicator_code_issues"]
        + type_results["year_issues"]
        + type_results["value_issues"]
    )
    if not all_type_issues:
        lines.append("All columns passed type consistency checks.")
        lines.append("")
    else:
        if type_results["country_code_issues"]:
            lines.append("**Country Code Issues:**")
            for issue in type_results["country_code_issues"]:
                lines.append(f"- {issue}")
            lines.append("")
        if type_results["indicator_code_issues"]:
            lines.append("**Indicator Code Issues:**")
            for issue in type_results["indicator_code_issues"]:
                lines.append(f"- {issue}")
            lines.append("")
        if type_results["year_issues"]:
            lines.append("**Year Issues:**")
            for issue in type_results["year_issues"]:
                lines.append(f"- {issue}")
            lines.append("")
        if type_results["value_issues"]:
            lines.append("**Value Issues:**")
            for issue in type_results["value_issues"]:
                lines.append(f"- {issue}")
            lines.append("")

    lines.append("---")
    lines.append("*Generated by DataQualityInspector using World Bank Open Data via wbgapi*")
    return "\n".join(lines)


def _build_html_report(
    schema: dict,
    null_results: dict,
    duplicate_results: dict,
    outlier_results: dict,
    type_results: dict,
    html_path: Path,
    generated_assets: dict[str, Path],
) -> str:
    """Build report content in HTML format."""
    summary_rows = _build_summary_rows(null_results, duplicate_results, outlier_results, type_results)

    null_rows = []
    for indicator_code, result in sorted(
        null_results["per_indicator"].items(),
        key=lambda item: item[1]["null_pct"],
        reverse=True,
    ):
        null_rows.append(
            "<tr>"
            f"<td>{escape(str(indicator_code))}</td>"
            f"<td>{result['total_rows']}</td>"
            f"<td>{result['null_count']}</td>"
            f"<td>{result['null_pct']}%</td>"
            f"<td>{escape(str(result['severity']))}</td>"
            "</tr>"
        )

    outlier_rows = []
    for indicator_code, result in sorted(
        outlier_results["per_indicator"].items(),
        key=lambda item: item[1]["outlier_count"],
        reverse=True,
    ):
        if result["status"] != "analysed":
            continue
        lower = f"{result['lower_bound']:.2e}" if result["lower_bound"] is not None else "N/A"
        upper = f"{result['upper_bound']:.2e}" if result["upper_bound"] is not None else "N/A"
        outlier_rows.append(
            "<tr>"
            f"<td>{escape(str(indicator_code))}</td>"
            f"<td>{result['outlier_count']}</td>"
            f"<td>{result['outlier_pct']}%</td>"
            f"<td>{lower}</td>"
            f"<td>{upper}</td>"
            "</tr>"
        )

    duplicate_example_rows = []
    for example in duplicate_results["examples"]:
        duplicate_example_rows.append(
            "<tr>"
            f"<td>{escape(str(example['country_code']))}</td>"
            f"<td>{escape(str(example['indicator_code']))}</td>"
            f"<td>{escape(str(example['year']))}</td>"
            "</tr>"
        )

    type_sections = []
    type_groups = [
        ("Country Code Issues", type_results["country_code_issues"]),
        ("Indicator Code Issues", type_results["indicator_code_issues"]),
        ("Year Issues", type_results["year_issues"]),
        ("Value Issues", type_results["value_issues"]),
    ]
    for title, issues in type_groups:
        if not issues:
            continue
        issue_items = "".join(f"<li>{escape(str(issue))}</li>" for issue in issues)
        type_sections.append(f"<h3>{escape(title)}</h3><ul>{issue_items}</ul>")

    visualizations_html = ""
    if generated_assets:
        visualization_blocks = []
        if "null_pct_chart" in generated_assets:
            rel_path = _relative_asset_path(html_path, generated_assets["null_pct_chart"])
            visualization_blocks.append(
                "<h3>Null Percentage by Indicator</h3>"
                f"<img src=\"{escape(rel_path)}\" alt=\"Null Percentage by Indicator\" />"
            )
        if "outlier_count_chart" in generated_assets:
            rel_path = _relative_asset_path(html_path, generated_assets["outlier_count_chart"])
            visualization_blocks.append(
                "<h3>Outlier Count by Indicator</h3>"
                f"<img src=\"{escape(rel_path)}\" alt=\"Outlier Count by Indicator\" />"
            )
        visualizations_html = "<h2>Visualizations</h2>" + "".join(visualization_blocks)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Data Quality Report</title>
  <style>
    body {{
      font-family: Arial, Helvetica, sans-serif;
      margin: 2rem auto;
      max-width: 1100px;
      line-height: 1.5;
      color: #1a1a1a;
      padding: 0 1rem;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      margin-bottom: 1.5rem;
    }}
    th, td {{
      border: 1px solid #ddd;
      padding: 0.5rem;
      text-align: left;
    }}
    th {{
      background: #f5f5f5;
    }}
    .status-pass {{
      color: #196127;
      font-weight: 700;
    }}
    .status-fail {{
      color: #9c1010;
      font-weight: 700;
    }}
    img {{
      max-width: 100%;
      height: auto;
      border: 1px solid #ddd;
      margin-bottom: 1rem;
    }}
    .meta li {{
      margin-bottom: 0.25rem;
    }}
  </style>
</head>
<body>
  <h1>Data Quality Report - World Bank Development Indicators</h1>

  <h2>Metadata</h2>
  <ul class="meta">
    <li>Source: World Bank Open Data API (wbgapi)</li>
    <li>Indicators: {schema["indicator_count"]}</li>
    <li>Year range: {schema["year_range"][0]}-{schema["year_range"][1]}</li>
    <li>Economies: {schema["economy_count"]} countries and regions</li>
    <li>Total rows: {schema["row_count"]}</li>
    <li>Generated: {escape(datetime.now().isoformat())}</li>
  </ul>

  <h3>Indicator List</h3>
  <ul>
    {''.join(f'<li>{escape(str(indicator))}</li>' for indicator in schema["indicators"])}
  </ul>

  <h2>Summary</h2>
  <table>
    <thead>
      <tr><th>Check</th><th>Status</th><th>Detail</th></tr>
    </thead>
    <tbody>
      {''.join(f'<tr><td>{escape(row["check"])}</td><td class="status-{"pass" if row["status"] == "pass" else "fail"}">{_status_mark(row["status"])}</td><td>{escape(row["detail"])}</td></tr>' for row in summary_rows)}
    </tbody>
  </table>

  <h2>Null Analysis</h2>
  <p>Overall null percentage: {null_results["overall_null_pct"]}% ({null_results["overall_null_count"]} of {null_results["total_rows"]} rows)</p>
  <table>
    <thead>
      <tr><th>Indicator</th><th>Total Rows</th><th>Null Count</th><th>Null %</th><th>Severity</th></tr>
    </thead>
    <tbody>
      {''.join(null_rows)}
    </tbody>
  </table>

  <h2>Duplicate Analysis</h2>
  <p>Duplicate count: {duplicate_results["duplicate_count"]} ({duplicate_results["duplicate_pct"]}% of {duplicate_results["total_rows"]} rows)</p>
  {('<table><thead><tr><th>Country Code</th><th>Indicator Code</th><th>Year</th></tr></thead><tbody>' + ''.join(duplicate_example_rows) + '</tbody></table>') if duplicate_example_rows else '<p>No duplicate records detected.</p>'}

  <h2>Outlier Analysis</h2>
  <p>Total outliers found: {outlier_results["total_outliers_found"]} across all indicators</p>
  <table>
    <thead>
      <tr><th>Indicator</th><th>Outlier Count</th><th>Outlier %</th><th>Lower Bound</th><th>Upper Bound</th></tr>
    </thead>
    <tbody>
      {''.join(outlier_rows)}
    </tbody>
  </table>
  {f'<p><strong>Note:</strong> {len(outlier_results["skipped_indicators"])} indicators skipped due to insufficient data (&lt; 30 non-null values): {escape(", ".join(outlier_results["skipped_indicators"]))}</p>' if outlier_results["skipped_indicators"] else ''}

  {visualizations_html}

  <h2>Type Consistency</h2>
  {('<p>All columns passed type consistency checks.</p>' if not type_sections else ''.join(type_sections))}

  <hr />
  <p><em>Generated by DataQualityInspector using World Bank Open Data via wbgapi</em></p>
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
    Generate a structured report summarizing data quality findings.

    Args:
        schema: Metadata about the fetched dataset.
        null_results: Results from null analysis check.
        duplicate_results: Results from duplicate detection check.
        outlier_results: Results from outlier detection check.
        type_results: Results from type consistency check.
        output_path: Path where the Markdown report will be written.
        html_output_path: Optional path for HTML output.
        assets_dir: Path where generated chart assets should be stored.
    """
    markdown_path = _ensure_parent_dir(output_path)
    html_path = _ensure_parent_dir(html_output_path) if html_output_path else None

    print(f"Writing Markdown report to {markdown_path}...")
    generated_assets = _generate_chart_assets(null_results, outlier_results, assets_dir)
    if generated_assets:
        print(f"Generated chart assets in {Path(assets_dir)}")

    markdown_content = _build_markdown_report(
        schema,
        null_results,
        duplicate_results,
        outlier_results,
        type_results,
        markdown_path,
        generated_assets,
    )
    markdown_path.write_text(markdown_content, encoding="utf-8")
    print(f"Done. Markdown report saved to {markdown_path}")

    if html_path is not None:
        print(f"Writing HTML report to {html_path}...")
        html_content = _build_html_report(
            schema,
            null_results,
            duplicate_results,
            outlier_results,
            type_results,
            html_path,
            generated_assets,
        )
        html_path.write_text(html_content, encoding="utf-8")
        print(f"Done. HTML report saved to {html_path}")
