"""Fetches World Bank Development Indicators using wbgapi."""

import hashlib
import json
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

import pandas as pd
import wbgapi as wb
from dqi.utils import timed
from dqi.console import console, get_progress, print_success, print_warning, print_error, print_info

INDICATORS = [
    'NY.GDP.MKTP.CD',
    'SP.POP.TOTL',
    'SE.ADT.LITR.ZS',
    'SH.DYN.MORT',
    'EG.ELC.ACCS.ZS',
    'IT.NET.USER.ZS',
    'SL.UEM.TOTL.ZS',
    'SP.DYN.LE00.IN',
    'AG.LND.ARBL.ZS',
    'EN.ATM.CO2E.PC',
]

START_YEAR = 2000
END_YEAR = 2023
CACHE_TTL_HOURS = 24
CACHE_DIR = Path(".cache") / "dqi"
FETCH_MAX_RETRIES = 3
FETCH_RETRY_BASE_DELAY_SECONDS = 2
FETCH_REQUEST_TIMEOUT_SECONDS = 45


def _build_cache_paths() -> tuple[Path, Path, Path]:
    """Return deterministic cache paths for current fetch config."""
    key_payload = {
        "indicators": sorted(INDICATORS),
        "start_year": START_YEAR,
        "end_year": END_YEAR,
    }
    cache_key = hashlib.sha256(json.dumps(key_payload, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    base_name = f"wb_{START_YEAR}_{END_YEAR}_{cache_key}"
    return (
        CACHE_DIR / f"{base_name}.parquet",
        CACHE_DIR / f"{base_name}.pkl",
        CACHE_DIR / f"{base_name}.json",
    )


def _build_schema(df_melted: pd.DataFrame) -> dict:
    """Build schema metadata from a fetched or cached DataFrame."""
    row_count = len(df_melted)
    indicator_count = df_melted["indicator_code"].nunique()
    economy_count = df_melted["country_code"].nunique()
    null_count = df_melted["value"].isna().sum()
    null_pct = round((null_count / row_count * 100) if row_count > 0 else 0.0, 2)
    return {
        "row_count": row_count,
        "indicator_count": indicator_count,
        "economy_count": economy_count,
        "year_range": [START_YEAR, END_YEAR],
        "indicators": INDICATORS,
        "columns": list(df_melted.columns),
        "null_count": null_count,
        "null_pct": null_pct,
    }


def _fetch_indicator_raw(indicator_code: str) -> pd.DataFrame:
    """Fetch one indicator from World Bank API."""
    return wb.data.DataFrame(
        [indicator_code],
        economy="all",
        time=range(START_YEAR, END_YEAR + 1),
        columns="series",
        numericTimeKeys=True,
    )


def _fetch_indicator_with_timeout(indicator_code: str) -> pd.DataFrame:
    """Fetch one indicator with hard timeout enforcement."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_fetch_indicator_raw, indicator_code)
        return future.result(timeout=FETCH_REQUEST_TIMEOUT_SECONDS)


def _fetch_raw_world_bank_data() -> tuple[pd.DataFrame, list[str]]:
    """
    Fetch raw World Bank data with chunked per-indicator requests and retry/backoff.

    Returns:
        tuple of (combined raw frame, failed indicator codes)
    """
    raw_frames: list[pd.DataFrame] = []
    failed_indicators: list[str] = []

    with get_progress() as progress:
        task = progress.add_task("[cyan]Fetching indicators from World Bank API...", total=len(INDICATORS))

        for index, indicator in enumerate(INDICATORS, start=1):
            last_exception: Exception | None = None
            progress.update(task, description=f"[cyan]Fetching {indicator}...")

            for attempt in range(1, FETCH_MAX_RETRIES + 1):
                try:
                    raw_frames.append(_fetch_indicator_with_timeout(indicator))
                    last_exception = None
                    break
                except FuturesTimeoutError as exc:  # pragma: no cover - depends on network/API behavior
                    last_exception = TimeoutError(
                        f"indicator {indicator} timed out after {FETCH_REQUEST_TIMEOUT_SECONDS}s"
                    )
                    if attempt < FETCH_MAX_RETRIES:
                        delay_seconds = FETCH_RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1))
                        progress.update(task, description=f"[yellow]Retrying {indicator} in {delay_seconds}s...")
                        time.sleep(delay_seconds)
                except Exception as exc:  # pragma: no cover - depends on network/API behavior
                    last_exception = exc
                    if attempt < FETCH_MAX_RETRIES:
                        delay_seconds = FETCH_RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1))
                        progress.update(task, description=f"[yellow]Retrying {indicator} (attempt {attempt + 1})...")
                        time.sleep(delay_seconds)

            if last_exception is not None:
                progress.console.print(f"[red]✗ Failed to fetch {indicator}: {last_exception}[/red]")
                failed_indicators.append(indicator)
            else:
                progress.console.print(f"[green]✓ {indicator}[/green]")

            progress.update(task, advance=1)

    if not raw_frames:
        raise RuntimeError(
            f"Failed to fetch all indicators. Failed indicator list: {failed_indicators}"
        )

    return pd.concat(raw_frames, axis=1), failed_indicators


@timed
def fetch_data(refresh_cache: bool = False) -> tuple[pd.DataFrame, dict]:
    """
    Fetch World Bank Development Indicators and reshape into long format.

    Returns:
        tuple: (DataFrame with columns country_code, indicator_code, year, value,
                schema dict with metadata about the fetched data)
    """
    parquet_path, pickle_path, metadata_path = _build_cache_paths()
    ttl_seconds = CACHE_TTL_HOURS * 3600
    cache_is_fresh = False

    cache_data_path: Path | None = None
    if parquet_path.exists():
        cache_data_path = parquet_path
    elif pickle_path.exists():
        cache_data_path = pickle_path

    if cache_data_path is not None and metadata_path.exists():
        file_age_seconds = time.time() - cache_data_path.stat().st_mtime
        cache_is_fresh = file_age_seconds <= ttl_seconds

    if not refresh_cache and cache_is_fresh:
        try:
            console.print(f"[blue]ℹ[/blue] Loading cached dataset from [cyan]{cache_data_path}[/cyan]...")
            if cache_data_path.suffix == ".parquet":
                df_cached = pd.read_parquet(cache_data_path)
            else:
                df_cached = pd.read_pickle(cache_data_path)
            schema = _build_schema(df_cached)
            print_success(
                f"Loaded {schema['row_count']:,} rows across "
                f"{schema['indicator_count']} indicators and {schema['economy_count']} economies."
            )
            return df_cached, schema
        except Exception as e:
            print_warning(f"Cache read failed ({e}). Falling back to fresh fetch.")

    console.print("\n[bold cyan]Fetching World Bank Data[/bold cyan]")
    console.print(f"[dim]Indicators: {len(INDICATORS)} | Years: {START_YEAR}-{END_YEAR}[/dim]\n")

    try:
        raw, failed_indicators = _fetch_raw_world_bank_data()
    except Exception as e:
        print_error(f"Failed to fetch data from World Bank API: {e}")
        console.print("[yellow]Please check your internet connection and try again.[/yellow]")
        raise SystemExit(1)

    # Flatten MultiIndex to columns
    df_long = raw.reset_index()

    # Rename columns
    df_long = df_long.rename(columns={"economy": "country_code", "time": "year"})

    # Melt indicator columns into long format
    df_melted = df_long.melt(
        id_vars=["country_code", "year"],
        var_name="indicator_code",
        value_name="value",
    )

    # Ensure correct dtypes
    df_melted["year"] = df_melted["year"].astype(int)
    df_melted["value"] = df_melted["value"].astype(float)

    # Defensive cleanup
    df_melted = df_melted.dropna(subset=["country_code", "indicator_code"], how="any")

    # Sort for deterministic outputs
    df_melted = df_melted.sort_values(["country_code", "indicator_code", "year"]).reset_index(drop=True)

    schema = _build_schema(df_melted)
    if failed_indicators:
        print_warning(f"{len(failed_indicators)} indicators failed and were omitted: {', '.join(failed_indicators)}")
    print_success(
        f"Fetched {schema['row_count']:,} rows across "
        f"{schema['indicator_count']} indicators and {schema['economy_count']} economies."
    )

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        df_melted.to_parquet(parquet_path, index=False)
        cache_format = "parquet"
        cache_path = parquet_path
    except Exception:
        df_melted.to_pickle(pickle_path)
        cache_format = "pickle"
        cache_path = pickle_path

    try:
        metadata_path.write_text(
            json.dumps(
                {
                    "created_at": int(time.time()),
                    "cache_ttl_hours": CACHE_TTL_HOURS,
                    "year_range": [START_YEAR, END_YEAR],
                    "indicators_requested": INDICATORS,
                    "indicators_failed": failed_indicators,
                    "cache_format": cache_format,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print_info(f"Cached dataset at {cache_path} ({cache_format})")
    except Exception as e:
        print_warning(f"Unable to write cache metadata ({e}).")

    return df_melted, schema
