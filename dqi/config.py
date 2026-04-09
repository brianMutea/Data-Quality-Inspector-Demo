"""Configuration constants for DataQualityInspector."""

# Null check thresholds
NULL_CRITICAL_THRESHOLD = 50  # Percentage above which nulls are critical
NULL_WARNING_THRESHOLD = 20   # Percentage above which nulls are a warning

# Outlier detection parameters
OUTLIER_MIN_DATA_POINTS = 30  # Minimum non-null values required for outlier analysis
OUTLIER_IQR_MULTIPLIER = 1.5  # IQR multiplier for outlier bounds (Q1 - k*IQR, Q3 + k*IQR)
OUTLIER_SAMPLE_SIZE = 5       # Number of sample outliers to include in results

# Duplicate check parameters
DUPLICATE_EXAMPLE_COUNT = 5   # Number of duplicate examples to include in results

# Outlier detection quantile parameters
OUTLIER_Q1_PERCENTILE = 0.25  # Lower quartile for IQR calculation
OUTLIER_Q3_PERCENTILE = 0.75  # Upper quartile for IQR calculation

# Type check parameters
YEAR_MIN = 2000  # Minimum valid year
YEAR_MAX = 2023  # Maximum valid year
COUNTRY_CODE_VALID_LENGTHS = [2, 3]  # Valid character lengths for country codes
INDICATOR_CODE_PATTERN = r'^[A-Z0-9]+(\.[A-Z0-9]+)+$'  # Expected indicator code format
