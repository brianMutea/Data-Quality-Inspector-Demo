"""Command-line interface for DataQualityInspector."""

import argparse

from dqi import __version__
from dqi.fetcher import fetch_data
from dqi.checks.nulls import check_nulls
from dqi.checks.duplicates import check_duplicates
from dqi.checks.outliers import check_outliers
from dqi.checks.types import check_types
from dqi.reporter import generate_report
from dqi.summary import build_summary_rows
from dqi.motto import random_motto
from dqi.console import (
    console,
    get_progress,
    print_header,
    print_error,
    create_summary_table,
    get_status_style,
)


def main() -> None:
    """Main entry point for the DataQualityInspector CLI."""
    parser = argparse.ArgumentParser(
        description="DataQualityInspector: Audit World Bank Development Indicators"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="reports/quality_report.md",
        help="Path for the Markdown report (default: reports/quality_report.md)",
    )
    parser.add_argument(
        "--html-output",
        type=str,
        default="reports/quality_report.html",
        help="Path for the HTML report (default: reports/quality_report.html)",
    )
    parser.add_argument(
        "--assets-dir",
        type=str,
        default="reports/assets",
        help="Directory where chart assets are saved (default: reports/assets)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Bypass local cache and fetch fresh data from the World Bank API",
    )
    parser.add_argument(
        "--motto",
        action="store_true",
        help="After a successful run, print a random tongue-in-cheek QA motto.",
    )

    args = parser.parse_args()

    try:
        print_header(
            "Data Quality Inspector",
            "Auditing World Bank Development Indicators",
        )

        df, schema = fetch_data(refresh_cache=args.refresh)

        check_steps = [
            ("Null Analysis", check_nulls, df),
            ("Duplicate Detection", check_duplicates, df),
            ("Outlier Detection", check_outliers, df),
            ("Type Consistency", check_types, df),
        ]

        console.print("\n[bold cyan]Running Data Quality Checks[/bold cyan]\n")

        results = {}
        with get_progress() as progress:
            overall_task = progress.add_task(
                "[bold cyan]Overall Progress",
                total=len(check_steps),
            )

            for step_name, check_func, check_data in check_steps:
                progress.update(overall_task, description=f"[cyan]Running {step_name}...")
                results[step_name] = check_func(check_data)
                progress.update(overall_task, advance=1)

        summary_rows = build_summary_rows(
            results["Null Analysis"],
            results["Duplicate Detection"],
            results["Outlier Detection"],
            results["Type Consistency"],
        )

        console.print("\n")
        table = create_summary_table()
        for row in summary_rows:
            cli_status = row.get("cli_status", row["status"])
            table.add_row(
                row["check"],
                get_status_style(cli_status),
                row["detail"],
            )
        console.print(table)

        console.print("\n[bold cyan]Generating Reports[/bold cyan]\n")
        generate_report(
            schema,
            results["Null Analysis"],
            results["Duplicate Detection"],
            results["Outlier Detection"],
            results["Type Consistency"],
            args.output,
            args.html_output,
            args.assets_dir,
        )

        console.print("\n[bold green]✓ Audit Complete![/bold green]")
        console.print(f"[dim]  Markdown: {args.output}[/dim]")
        console.print(f"[dim]  HTML:     {args.html_output}[/dim]")

        if args.motto:
            console.print(f"\n[italic dim]{random_motto()}[/italic dim]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Audit cancelled.[/yellow]")
        raise SystemExit(0)
    except Exception as e:
        print_error(f"Audit failed: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
