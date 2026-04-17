"""Command-line interface for DataQualityInspector."""

import argparse
from dqi.fetcher import fetch_data
from dqi.checks.nulls import check_nulls
from dqi.checks.duplicates import check_duplicates
from dqi.checks.outliers import check_outliers
from dqi.checks.types import check_types
from dqi.reporter import generate_report
from dqi.console import (
    console,
    get_progress,
    print_header,
    print_success,
    print_warning,
    print_error,
    print_info,
    create_summary_table,
    get_status_style,
)


def main() -> None:
    """Main entry point for the DataQualityInspector CLI."""
    parser = argparse.ArgumentParser(
        description='DataQualityInspector: Audit World Bank Development Indicators'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='reports/quality_report.md',
        help='Path for the Markdown report (default: reports/quality_report.md)'
    )
    parser.add_argument(
        '--html-output',
        type=str,
        default='reports/quality_report.html',
        help='Path for the HTML report (default: reports/quality_report.html)'
    )
    parser.add_argument(
        '--assets-dir',
        type=str,
        default='reports/assets',
        help='Directory where chart assets are saved (default: reports/assets)'
    )
    parser.add_argument(
        '--refresh',
        action='store_true',
        help='Bypass local cache and fetch fresh data from the World Bank API'
    )

    args = parser.parse_args()

    try:
        # Print header
        print_header(
            "Data Quality Inspector",
            "Auditing World Bank Development Indicators"
        )

        # Step 1: Fetch data
        df, schema = fetch_data(refresh_cache=args.refresh)

        # Define check steps for progress tracking
        check_steps = [
            ("Null Analysis", check_nulls, df),
            ("Duplicate Detection", check_duplicates, df),
            ("Outlier Detection", check_outliers, df),
            ("Type Consistency", check_types, df),
        ]

        # Run checks with overall progress
        console.print("\n[bold cyan]Running Data Quality Checks[/bold cyan]\n")

        results = {}
        with get_progress() as progress:
            overall_task = progress.add_task(
                "[bold cyan]Overall Progress",
                total=len(check_steps)
            )

            for step_name, check_func, check_data in check_steps:
                progress.update(overall_task, description=f"[cyan]Running {step_name}...")
                results[step_name] = check_func(check_data)
                progress.update(overall_task, advance=1)

        # Display summary table
        console.print("\n")
        table = create_summary_table()

        type_issues = (
            results["Type Consistency"]["country_code_issues"]
            + results["Type Consistency"]["indicator_code_issues"]
            + results["Type Consistency"]["year_issues"]
            + results["Type Consistency"]["value_issues"]
        )

        # Null status
        if results["Null Analysis"]["critical_indicators"]:
            null_status = get_status_style("critical")
            null_detail = f"{len(results['Null Analysis']['critical_indicators'])} critical"
        elif results["Null Analysis"]["warning_indicators"]:
            null_status = get_status_style("warn")
            null_detail = f"{len(results['Null Analysis']['warning_indicators'])} warning"
        else:
            null_status = get_status_style("pass")
            null_detail = f"{results['Null Analysis']['overall_null_pct']}% nulls"

        table.add_row("Null Analysis", null_status, null_detail)

        # Duplicate status
        dup_count = results["Duplicate Detection"]["duplicate_count"]
        dup_pct = results["Duplicate Detection"]["duplicate_pct"]
        dup_status = get_status_style("pass" if dup_count == 0 else "fail")
        table.add_row("Duplicates", dup_status, f"{dup_count} ({dup_pct}%)")

        # Outlier status
        outlier_count = results["Outlier Detection"]["total_outliers_found"]
        outlier_status = get_status_style("pass" if outlier_count == 0 else "analysed")
        table.add_row("Outlier Analysis", outlier_status, f"{outlier_count} found")

        # Type status
        type_status = get_status_style("pass" if not type_issues else "fail")
        type_detail = f"{len(type_issues)} issues" if type_issues else "All passed"
        table.add_row("Type Consistency", type_status, type_detail)

        console.print(table)

        # Step 6: Generate report
        console.print("\n[bold cyan]Generating Reports[/bold cyan]\n")
        generate_report(
            schema,
            results["Null Analysis"],
            results["Duplicate Detection"],
            results["Outlier Detection"],
            results["Type Consistency"],
            args.output,
            args.html_output,
            args.assets_dir
        )

        # Final success message
        console.print("\n[bold green]✓ Audit Complete![/bold green]")
        console.print(f"[dim]  Markdown: {args.output}[/dim]")
        console.print(f"[dim]  HTML:     {args.html_output}[/dim]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Audit cancelled.[/yellow]")
        raise SystemExit(0)
    except Exception as e:
        print_error(f"Audit failed: {e}")
        raise SystemExit(1)


if __name__ == '__main__':
    main()
