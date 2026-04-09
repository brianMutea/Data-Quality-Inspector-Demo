"""Command-line interface for DataQualityInspector."""

import argparse

from dqi.checks.duplicates import check_duplicates
from dqi.checks.nulls import check_nulls
from dqi.checks.outliers import check_outliers
from dqi.checks.types import check_types
from dqi.fetcher import fetch_data
from dqi.reporter import generate_report


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="DataQualityInspector: Audit World Bank Development Indicators"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="quality_report.md",
        help="Path for the Markdown report (default: quality_report.md)",
    )
    parser.add_argument(
        "--html-output",
        type=str,
        default=None,
        help="Optional path for an HTML report output (default: disabled)",
    )
    parser.add_argument(
        "--assets-dir",
        type=str,
        default="reports/assets",
        help="Directory for generated chart assets (default: reports/assets)",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Bypass local cache and fetch fresh data from the World Bank API",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the DataQualityInspector CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        # Step 1: Fetch data
        df, schema = fetch_data(refresh_cache=args.refresh)
        print()

        # Step 2: Null check
        null_results = check_nulls(df)
        print()

        # Step 3: Duplicate check
        duplicate_results = check_duplicates(df)
        print()

        # Step 4: Outlier check
        outlier_results = check_outliers(df)
        print()

        # Step 5: Type check
        type_results = check_types(df)
        print()

        # Step 6: Generate report(s)
        generate_report(
            schema,
            null_results,
            duplicate_results,
            outlier_results,
            type_results,
            args.output,
            html_output_path=args.html_output,
            assets_dir=args.assets_dir,
        )

        if args.html_output:
            print(
                f"\nAudit complete. Open {args.output} (Markdown) "
                f"and {args.html_output} (HTML) to view your reports."
            )
        else:
            print(f"\nAudit complete. Open {args.output} to view your report.")

    except KeyboardInterrupt:
        print("\nAudit cancelled.")
        raise SystemExit(0)


if __name__ == "__main__":
    main()
