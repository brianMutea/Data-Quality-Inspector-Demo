"""Command-line interface for DataQualityInspector."""

import argparse
from dqi.fetcher import fetch_data
from dqi.checks.nulls import check_nulls
from dqi.checks.duplicates import check_duplicates
from dqi.checks.outliers import check_outliers
from dqi.checks.types import check_types
from dqi.reporter import generate_report


def main() -> None:
    """Main entry point for the DataQualityInspector CLI."""
    parser = argparse.ArgumentParser(
        description='DataQualityInspector: Audit World Bank Development Indicators'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='quality_report.md',
        help='Path for the Markdown report (default: quality_report.md)'
    )
    parser.add_argument(
        '--refresh',
        action='store_true',
        help='Bypass local cache and fetch fresh data from the World Bank API'
    )
    
    args = parser.parse_args()
    
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
        
        # Step 6: Generate report
        generate_report(
            schema,
            null_results,
            duplicate_results,
            outlier_results,
            type_results,
            args.output
        )
        
        print(f"\nAudit complete. Open {args.output} to view your report.")
        
    except KeyboardInterrupt:
        print("\nAudit cancelled.")
        raise SystemExit(0)


if __name__ == '__main__':
    main()
