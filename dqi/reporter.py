"""Generate Markdown and HTML reports from quality check results."""

from datetime import datetime
from pathlib import Path
from typing import Optional
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def _generate_null_chart(null_results: dict, assets_dir: Path) -> str:
    """Generate a bar chart for null percentages by indicator."""
    sorted_indicators = sorted(
        null_results['per_indicator'].items(),
        key=lambda x: x[1]['null_pct'],
        reverse=True
    )
    
    indicators = [item[0] for item in sorted_indicators]
    null_pcts = [item[1]['null_pct'] for item in sorted_indicators]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(indicators, null_pcts)
    
    for i, (bar, pct) in enumerate(zip(bars, null_pcts)):
        if pct > 50:
            bar.set_color('#dc3545')
        elif pct >= 20:
            bar.set_color('#ffc107')
        else:
            bar.set_color('#28a745')
    
    ax.set_xlabel('Null Percentage (%)')
    ax.set_title('Null Values by Indicator')
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    chart_path = assets_dir / 'null_analysis.png'
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return chart_path.name


def _generate_outlier_chart(outlier_results: dict, assets_dir: Path) -> str:
    """Generate a bar chart for outlier counts by indicator."""
    analyzed_indicators = {
        code: result for code, result in outlier_results['per_indicator'].items()
        if result['status'] == 'analysed'
    }
    
    sorted_indicators = sorted(
        analyzed_indicators.items(),
        key=lambda x: x[1]['outlier_count'],
        reverse=True
    )
    
    indicators = [item[0] for item in sorted_indicators]
    outlier_counts = [item[1]['outlier_count'] for item in sorted_indicators]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(indicators, outlier_counts, color='#17a2b8')
    ax.set_xlabel('Outlier Count')
    ax.set_title('Outliers Detected by Indicator')
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    
    chart_path = assets_dir / 'outlier_analysis.png'
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    return chart_path.name


def generate_report(
    schema: dict,
    null_results: dict,
    duplicate_results: dict,
    outlier_results: dict,
    type_results: dict,
    output_path: str,
    html_output: Optional[str] = None,
    assets_dir: Optional[str] = None
) -> None:
    """
    Generate a structured Markdown report summarizing data quality findings.
    
    Args:
        schema: Metadata about the fetched dataset
        null_results: Results from null analysis check
        duplicate_results: Results from duplicate detection check
        outlier_results: Results from outlier detection check
        type_results: Results from type consistency check
        output_path: Path where the Markdown report will be written
        html_output: Optional path for HTML report output
        assets_dir: Optional directory for chart assets (PNG files)
    """
    print(f"Writing report to {output_path}...")
    
    chart_null = None
    chart_outlier = None
    
    if assets_dir:
        assets_path = Path(assets_dir)
        assets_path.mkdir(parents=True, exist_ok=True)
        print(f"Generating charts in {assets_dir}...")
        chart_null = _generate_null_chart(null_results, assets_path)
        chart_outlier = _generate_outlier_chart(outlier_results, assets_path)
        print(f"Charts saved to {assets_dir}")
    
    lines = []
    
    # Header
    lines.append("# Data Quality Report — World Bank Development Indicators")
    lines.append("")
    
    # Metadata
    lines.append("**Metadata:**")
    lines.append("")
    lines.append("- Source: World Bank Open Data API (wbgapi)")
    lines.append(f"- Indicators: {schema['indicator_count']}")
    for indicator in schema['indicators']:
        lines.append(f"  - {indicator}")
    lines.append(f"- Year range: {schema['year_range'][0]}–{schema['year_range'][1]}")
    lines.append(f"- Economies: {schema['economy_count']} countries and regions")
    lines.append(f"- Total rows: {schema['row_count']}")
    lines.append(f"- Generated: {datetime.now().isoformat()}")
    lines.append("")
    
    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Check | Status | Detail |")
    lines.append("|-------|--------|--------|")
    
    # Null Analysis status
    if null_results['critical_indicators']:
        null_status = "❌"
        null_detail = f"{len(null_results['critical_indicators'])} critical indicators"
    elif null_results['warning_indicators']:
        null_status = "❌"
        null_detail = f"{len(null_results['warning_indicators'])} warning indicators"
    else:
        null_status = "✅"
        null_detail = f"{null_results['overall_null_pct']}% nulls overall"
    lines.append(f"| Null Analysis | {null_status} | {null_detail} |")
    
    # Duplicates status
    dup_status = "✅" if duplicate_results['verdict'] == 'pass' else "❌"
    dup_detail = f"{duplicate_results['duplicate_count']} duplicates ({duplicate_results['duplicate_pct']}%)"
    lines.append(f"| Duplicates | {dup_status} | {dup_detail} |")
    
    # Outlier Analysis status
    outlier_status = "✅"
    outlier_detail = f"{outlier_results['total_outliers_found']} outliers found"
    lines.append(f"| Outlier Analysis | {outlier_status} | {outlier_detail} |")
    
    # Type Consistency status
    type_status = "✅" if type_results['verdict'] == 'pass' else "❌"
    all_issues = (type_results['country_code_issues'] + type_results['indicator_code_issues'] +
                  type_results['year_issues'] + type_results['value_issues'])
    type_detail = f"{len(all_issues)} issues found" if all_issues else "All checks passed"
    lines.append(f"| Type Consistency | {type_status} | {type_detail} |")
    
    lines.append("")
    
    # Null Analysis
    lines.append("## Null Analysis")
    lines.append("")
    
    if chart_null and assets_dir:
        lines.append(f"![Null Analysis Chart]({Path(assets_dir).name}/{chart_null})")
        lines.append("")
    
    lines.append(f"Overall null percentage: {null_results['overall_null_pct']}% ({null_results['overall_null_count']} of {null_results['total_rows']} rows)")
    lines.append("")
    lines.append("| Indicator | Total Rows | Null Count | Null % | Severity |")
    lines.append("|-----------|------------|------------|--------|----------|")
    
    # Sort by null_pct descending
    sorted_indicators = sorted(
        null_results['per_indicator'].items(),
        key=lambda x: x[1]['null_pct'],
        reverse=True
    )
    
    for indicator_code, result in sorted_indicators:
        lines.append(f"| {indicator_code} | {result['total_rows']} | {result['null_count']} | {result['null_pct']}% | {result['severity']} |")
    
    lines.append("")
    critical_count = len(null_results['critical_indicators'])
    warning_count = len(null_results['warning_indicators'])
    lines.append(f"{critical_count} critical and {warning_count} warning indicators identified.")
    lines.append("")
    
    # Duplicate Analysis
    lines.append("## Duplicate Analysis")
    lines.append("")
    lines.append(f"Duplicate count: {duplicate_results['duplicate_count']} ({duplicate_results['duplicate_pct']}% of {duplicate_results['total_rows']} rows)")
    lines.append("")
    
    if duplicate_results['duplicate_count'] > 0:
        lines.append("**Examples:**")
        lines.append("")
        lines.append("| Country Code | Indicator Code | Year |")
        lines.append("|--------------|----------------|------|")
        for example in duplicate_results['examples']:
            lines.append(f"| {example['country_code']} | {example['indicator_code']} | {example['year']} |")
        lines.append("")
    else:
        lines.append("No duplicate records detected.")
        lines.append("")
    
    # Outlier Analysis
    lines.append("## Outlier Analysis")
    lines.append("")
    
    if chart_outlier and assets_dir:
        lines.append(f"![Outlier Analysis Chart]({Path(assets_dir).name}/{chart_outlier})")
        lines.append("")
    
    lines.append(f"Total outliers found: {outlier_results['total_outliers_found']} across all indicators")
    lines.append("")
    lines.append("| Indicator | Outlier Count | Outlier % | Lower Bound | Upper Bound |")
    lines.append("|-----------|---------------|-----------|-------------|-------------|")
    
    # Sort by outlier_count descending
    sorted_outliers = sorted(
        outlier_results['per_indicator'].items(),
        key=lambda x: x[1]['outlier_count'],
        reverse=True
    )
    
    for indicator_code, result in sorted_outliers:
        if result['status'] == 'analysed':
            lower = f"{result['lower_bound']:.2e}" if result['lower_bound'] is not None else "N/A"
            upper = f"{result['upper_bound']:.2e}" if result['upper_bound'] is not None else "N/A"
            lines.append(f"| {indicator_code} | {result['outlier_count']} | {result['outlier_pct']}% | {lower} | {upper} |")
    
    lines.append("")
    
    if outlier_results['skipped_indicators']:
        lines.append(f"**Note:** {len(outlier_results['skipped_indicators'])} indicators skipped due to insufficient data (< 30 non-null values): {', '.join(outlier_results['skipped_indicators'])}")
        lines.append("")
    
    # Type Consistency
    lines.append("## Type Consistency")
    lines.append("")
    
    all_issues = (type_results['country_code_issues'] + type_results['indicator_code_issues'] +
                  type_results['year_issues'] + type_results['value_issues'])
    
    if not all_issues:
        lines.append("All columns passed type consistency checks.")
        lines.append("")
    else:
        if type_results['country_code_issues']:
            lines.append("**Country Code Issues:**")
            for issue in type_results['country_code_issues']:
                lines.append(f"- {issue}")
            lines.append("")
        
        if type_results['indicator_code_issues']:
            lines.append("**Indicator Code Issues:**")
            for issue in type_results['indicator_code_issues']:
                lines.append(f"- {issue}")
            lines.append("")
        
        if type_results['year_issues']:
            lines.append("**Year Issues:**")
            for issue in type_results['year_issues']:
                lines.append(f"- {issue}")
            lines.append("")
        
        if type_results['value_issues']:
            lines.append("**Value Issues:**")
            for issue in type_results['value_issues']:
                lines.append(f"- {issue}")
            lines.append("")
    
    # Footer
    lines.append("---")
    lines.append("*Generated by DataQualityInspector using World Bank Open Data via wbgapi*")
    
    # Write Markdown to file
    markdown_content = '\n'.join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Done. Report saved to {output_path}")
    
    # Generate HTML if requested
    if html_output:
        _generate_html_report(markdown_content, html_output, assets_dir)
        print(f"HTML report saved to {html_output}")


def _generate_html_report(markdown_content: str, html_path: str, assets_dir: Optional[str]) -> None:
    """Convert Markdown report to HTML with styling."""
    html_lines = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>Data Quality Report - World Bank Development Indicators</title>',
        '    <style>',
        '        body {',
        '            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;',
        '            line-height: 1.6;',
        '            max-width: 1200px;',
        '            margin: 0 auto;',
        '            padding: 20px;',
        '            background-color: #f5f5f5;',
        '        }',
        '        .container {',
        '            background-color: white;',
        '            padding: 40px;',
        '            border-radius: 8px;',
        '            box-shadow: 0 2px 4px rgba(0,0,0,0.1);',
        '        }',
        '        h1 {',
        '            color: #2c3e50;',
        '            border-bottom: 3px solid #3498db;',
        '            padding-bottom: 10px;',
        '        }',
        '        h2 {',
        '            color: #34495e;',
        '            margin-top: 30px;',
        '            border-bottom: 2px solid #ecf0f1;',
        '            padding-bottom: 8px;',
        '        }',
        '        table {',
        '            width: 100%;',
        '            border-collapse: collapse;',
        '            margin: 20px 0;',
        '        }',
        '        th, td {',
        '            padding: 12px;',
        '            text-align: left;',
        '            border: 1px solid #ddd;',
        '        }',
        '        th {',
        '            background-color: #3498db;',
        '            color: white;',
        '            font-weight: 600;',
        '        }',
        '        tr:nth-child(even) {',
        '            background-color: #f8f9fa;',
        '        }',
        '        img {',
        '            max-width: 100%;',
        '            height: auto;',
        '            margin: 20px 0;',
        '            border-radius: 4px;',
        '            box-shadow: 0 2px 4px rgba(0,0,0,0.1);',
        '        }',
        '        ul {',
        '            margin: 10px 0;',
        '        }',
        '        li {',
        '            margin: 5px 0;',
        '        }',
        '        hr {',
        '            border: none;',
        '            border-top: 1px solid #ddd;',
        '            margin: 30px 0;',
        '        }',
        '        .metadata {',
        '            background-color: #ecf0f1;',
        '            padding: 15px;',
        '            border-radius: 4px;',
        '            margin: 20px 0;',
        '        }',
        '    </style>',
        '</head>',
        '<body>',
        '    <div class="container">',
    ]
    
    for line in markdown_content.split('\n'):
        line = line.strip()
        
        if line.startswith('# '):
            html_lines.append(f'        <h1>{line[2:]}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'        <h2>{line[3:]}</h2>')
        elif line.startswith('**') and line.endswith('**'):
            html_lines.append(f'        <p><strong>{line[2:-2]}</strong></p>')
        elif line.startswith('!['):
            alt_end = line.find(']')
            url_start = line.find('(', alt_end)
            url_end = line.find(')', url_start)
            if alt_end > 0 and url_start > 0 and url_end > 0:
                alt_text = line[2:alt_end]
                img_url = line[url_start+1:url_end]
                html_lines.append(f'        <img src="{img_url}" alt="{alt_text}">')
        elif line.startswith('|') and '---' in line:
            continue
        elif line.startswith('|'):
            if '<table>' not in '\n'.join(html_lines[-5:]):
                html_lines.append('        <table>')
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                html_lines.append('            <thead><tr>')
                for cell in cells:
                    html_lines.append(f'                <th>{cell}</th>')
                html_lines.append('            </tr></thead>')
                html_lines.append('            <tbody>')
            else:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                html_lines.append('            <tr>')
                for cell in cells:
                    html_lines.append(f'                <td>{cell}</td>')
                html_lines.append('            </tr>')
        elif line.startswith('- '):
            if '<ul>' not in '\n'.join(html_lines[-3:]):
                html_lines.append('        <ul>')
            html_lines.append(f'            <li>{line[2:]}</li>')
        elif line == '---':
            html_lines.append('        <hr>')
        elif line.startswith('*') and line.endswith('*') and not line.startswith('**'):
            html_lines.append(f'        <p><em>{line[1:-1]}</em></p>')
        elif line:
            if html_lines[-1].strip().endswith('</ul>') or html_lines[-1].strip().endswith('</table>'):
                pass
            elif '<ul>' in '\n'.join(html_lines[-5:]) and '</ul>' not in '\n'.join(html_lines[-3:]):
                html_lines.append('        </ul>')
                html_lines.append(f'        <p>{line}</p>')
            elif '<table>' in '\n'.join(html_lines[-20:]) and '</table>' not in '\n'.join(html_lines[-3:]):
                html_lines.append('            </tbody>')
                html_lines.append('        </table>')
                html_lines.append(f'        <p>{line}</p>')
            else:
                html_lines.append(f'        <p>{line}</p>')
    
    if '<ul>' in '\n'.join(html_lines[-10:]) and '</ul>' not in '\n'.join(html_lines[-3:]):
        html_lines.append('        </ul>')
    if '<table>' in '\n'.join(html_lines[-30:]) and '</table>' not in '\n'.join(html_lines[-3:]):
        html_lines.append('            </tbody>')
        html_lines.append('        </table>')
    
    html_lines.extend([
        '    </div>',
        '</body>',
        '</html>'
    ])
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines))
