# DataQualityInspector

A professional CLI tool that fetches World Development Indicators from the World Bank API, performs comprehensive data quality audits, and generates detailed Markdown and HTML reports with visualization assets. Perfect for data analysts, researchers, and developers working with World Bank datasets.

## Overview

DataQualityInspector automates the entire data quality assessment workflow:

1. **Data Fetching**: Retrieves 10 key World Development Indicators for all countries and regions (2000-2023) via the World Bank Open Data API
2. **Data Transformation**: Reshapes raw API data into clean, analysis-ready long-format DataFrames
3. **Quality Checks**: Runs four comprehensive data quality audits
4. **Report Generation**: Creates structured Markdown and optional HTML reports with chart assets

## Features

### Report Outputs

- **Markdown report** (`--output`) for lightweight sharing and version control
- **HTML report** (`--html-output`) for browser-friendly presentation
- **Chart assets** (`--assets-dir`) generated under `reports/assets` by default:
  - Null percentage by indicator
  - Outlier count by indicator

### Data Quality Checks

**Null Analysis**
- Calculates overall null percentage across the dataset
- Groups null analysis by indicator for granular insights
- Flags indicators with critical (>50%) or warning (≥20%) null rates
- Provides severity levels: critical, warning, or ok

**Duplicate Detection**
- Identifies duplicate records based on country + indicator + year combinations
- Reports duplicate count and percentage
- Provides examples of duplicate records for investigation

**Outlier Detection**
- Uses the IQR (Interquartile Range) method for statistical outlier detection
- Analyzes each indicator independently to account for different value scales
- Calculates lower and upper bounds (Q1 - 1.5×IQR, Q3 + 1.5×IQR)
- Skips indicators with insufficient data (<30 non-null values)
- Provides sample outlier values for review

**Type Consistency**
- Validates country codes (2-3 character format)
- Checks indicator code format (dot-separated uppercase alphanumeric)
- Ensures year values are integers within 2000-2023 range
- Verifies value column contains numeric data
- Detects null values, empty strings, and format violations

### Indicators Analyzed

The tool fetches these 10 World Development Indicators:

- `NY.GDP.MKTP.CD` - GDP (current US$)
- `SP.POP.TOTL` - Population, total
- `SE.ADT.LITR.ZS` - Literacy rate, adult total (% of people ages 15 and above)
- `SH.DYN.MORT` - Mortality rate, under-5 (per 1,000 live births)
- `EG.ELC.ACCS.ZS` - Access to electricity (% of population)
- `IT.NET.USER.ZS` - Individuals using the Internet (% of population)
- `SL.UEM.TOTL.ZS` - Unemployment, total (% of total labor force)
- `SP.DYN.LE00.IN` - Life expectancy at birth, total (years)
- `AG.LND.ARBL.ZS` - Arable land (% of land area)
- `EN.ATM.CO2E.PC` - CO2 emissions (metric tons per capita)

## Requirements

- Python 3.10 or later
- Internet connection (required for World Bank API access)

## Installation

### Step 1: Clone or Download the Project

```bash
cd /home/brianm/DataQualityInspector
```

### Step 2: Create a Virtual Environment

```bash
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment

```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `wbgapi` - World Bank API client
- `matplotlib` - Chart generation for report assets
- `pytest` - Testing framework

## Usage

### Basic Usage

Run the audit with default settings (outputs to `quality_report.md` and chart assets under `reports/assets`):

```bash
python -m dqi.cli
```

### Custom Markdown Output Path

Specify a custom location for the report:

```bash
python -m dqi.cli --output reports/quality_report.md
```

### Generate Markdown + HTML Outputs

Generate both report formats and explicitly choose the asset directory:

```bash
python -m dqi.cli \
  --output reports/quality_report.md \
  --html-output reports/quality_report.html \
  --assets-dir reports/assets
```

### What Happens When You Run It

1. **Fetching Data**: The tool connects to the World Bank API and downloads indicator data
   ```
   Fetching World Bank data for 10 indicators (2000-2023)...
   Fetched 65280 rows across 10 indicators and 272 economies.
   ```

2. **Running Checks**: Each quality check runs sequentially with progress updates
   ```
   Running null check...
   Running duplicate check...
   Running outlier check...
   Outlier check: 1/10 indicators processed...
   Running type consistency check...
   ```

3. **Generating Report**: A Markdown report is created at the specified path, optional HTML is written when requested, and chart assets are generated
   ```
   Writing Markdown report to quality_report.md...
   Generated chart assets in reports/assets
   Done. Markdown report saved to quality_report.md
   Writing HTML report to reports/quality_report.html...
   Done. HTML report saved to reports/quality_report.html
   
   Audit complete. Open quality_report.md (Markdown) and reports/quality_report.html (HTML) to view your reports.
   ```

### Understanding the Report

The generated reports include:

- **Metadata Section**: Dataset overview with row counts, indicator list, and timestamp
- **Summary Table**: Quick status overview with ✅/❌ indicators for each check
- **Null Analysis**: Detailed table showing null percentages per indicator with severity levels
- **Duplicate Analysis**: Count and examples of duplicate records
- **Outlier Analysis**: Statistical bounds and outlier counts per indicator
- **Type Consistency**: Issues found in column formats and data types
- **Visualizations**: Embedded chart images generated into `reports/assets`

## Development

### Running Tests

Execute the full test suite:

```bash
pytest tests/
```

Run tests with verbose output:

```bash
pytest tests/ -v
```

With project-local configuration:

```bash
pytest -q
```

Run a specific test file:

```bash
pytest tests/test_nulls.py
```

### Project Structure

```
DataQualityInspector/
├── dqi/                      # Main package
│   ├── __init__.py
│   ├── cli.py               # Command-line interface
│   ├── fetcher.py           # World Bank API data fetching
│   ├── reporter.py          # Markdown + HTML report generation
│   └── checks/              # Quality check modules
│       ├── __init__.py
│       ├── duplicates.py    # Duplicate detection
│       ├── nulls.py         # Null analysis
│       ├── outliers.py      # Outlier detection (IQR method)
│       └── types.py         # Type consistency validation
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── test_cli.py
│   ├── test_duplicates.py
│   ├── test_fetcher.py
│   ├── test_nulls.py
│   ├── test_outliers.py
│   └── test_reporter.py
├── reports/                 # Default output directory
│   └── assets/              # Generated chart image assets
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Troubleshooting

**API Connection Issues**
- Ensure you have an active internet connection
- The World Bank API may occasionally be slow or unavailable
- If fetching fails, wait a moment and try again

**Import Errors**
- Make sure your virtual environment is activated: `source venv/bin/activate`
- Verify all dependencies are installed: `pip install -r requirements.txt`

**Permission Errors**
- Ensure you have write permissions for the output directory
- The default output is the current directory; use `--output` to specify another location

**Generated Artifacts**
- Do not commit generated report artifacts (for example `reports/*.md`, `reports/*.html`, `reports/assets/*`) or Python caches such as `__pycache__/`.

## License

This project is open source and available for educational and research purposes.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the tool.
