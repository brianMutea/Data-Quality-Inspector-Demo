"""Generate Markdown report from quality check results."""

from datetime import datetime


def generate_report(
    schema: dict,
    null_results: dict,
    duplicate_results: dict,
    outlier_results: dict,
    type_results: dict,
    output_path: str
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
    """
    print(f"Writing report to {output_path}...")
    
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
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"Done. Report saved to {output_path}")
