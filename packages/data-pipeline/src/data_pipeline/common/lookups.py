"""Lookup data utilities: ZIP-to-FIPS crosswalk and county population."""

import json
from io import BytesIO
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

# Cache directory for downloaded lookup data
# Located under the book's data directory
PROJECT_ROOT = Path(__file__).parents[5]  # Up to reading-data-companion/
CACHE_DIR = PROJECT_ROOT / "books" / "the-grid" / "data" / "cache"

# Census Bureau ZCTA-to-County Relationship File (2020)
# https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.html
CENSUS_ZCTA_COUNTY_URL = (
    "https://www2.census.gov/geo/docs/maps-data/data/rel2020/zcta520/tab20_zcta520_county20_natl.txt"
)

# Census Population Estimates (direct CSV downloads, no API key needed)
CENSUS_POP_URLS = {
    "2010s": "https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv",
    "2020s": "https://www2.census.gov/programs-surveys/popest/datasets/2020-2023/counties/totals/co-est2023-alldata.csv",
}


def _ensure_cache_dir() -> Path:
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR


def download_zip_to_fips(force: bool = False) -> pd.DataFrame:
    """Download the Census Bureau ZCTA-to-County crosswalk.

    Args:
        force: If True, re-download even if cached.

    Returns:
        DataFrame with columns: zip, fips, county, area_ratio
        (area_ratio = land area ratio for ZIPs spanning counties)
    """
    cache_path = _ensure_cache_dir() / "zip_county_crosswalk.csv"

    if cache_path.exists() and not force:
        return pd.read_csv(cache_path, dtype={"zip": str, "fips": str})

    print("Downloading ZCTA-County crosswalk from Census Bureau...")
    response = requests.get(CENSUS_ZCTA_COUNTY_URL)
    response.raise_for_status()

    # Census file is pipe-delimited
    df = pd.read_csv(
        BytesIO(response.content),
        sep="|",
        dtype={"GEOID_ZCTA5_20": str, "GEOID_COUNTY_20": str},
        encoding="utf-8-sig",  # Handle BOM
    )

    # Filter to rows that have ZCTA data (some rows are county-only)
    df = df[df["GEOID_ZCTA5_20"].notna() & (df["GEOID_ZCTA5_20"] != "")]

    # Calculate area ratio for each ZCTA-county pair
    zcta_total_area = df.groupby("GEOID_ZCTA5_20")["AREALAND_PART"].transform("sum")
    df["area_ratio"] = df["AREALAND_PART"] / zcta_total_area

    # Standardize column names
    df = df.rename(columns={
        "GEOID_ZCTA5_20": "zip",
        "GEOID_COUNTY_20": "fips",
        "NAMELSAD_COUNTY_20": "county",
    })

    # Keep relevant columns
    df = df[["zip", "fips", "county", "area_ratio"]]

    # Ensure codes are properly formatted
    df["zip"] = df["zip"].str.zfill(5)
    df["fips"] = df["fips"].str.zfill(5)

    # Cache for future use
    df.to_csv(cache_path, index=False)
    print(f"Cached crosswalk to {cache_path}")

    return df


def load_zip_to_fips(cache_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the ZIP-to-FIPS crosswalk from cache.

    Args:
        cache_path: Optional custom cache path.

    Returns:
        DataFrame with ZIP-to-FIPS mapping.

    Raises:
        FileNotFoundError: If crosswalk hasn't been downloaded.
    """
    path = cache_path or (CACHE_DIR / "zip_county_crosswalk.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"Crosswalk not found at {path}. Run download_zip_to_fips() first."
        )
    return pd.read_csv(path, dtype={"zip": str, "fips": str})


def download_county_population(
    years: list[int],
    force: bool = False,
) -> pd.DataFrame:
    """Download county population from Census population estimates.

    Args:
        years: List of years to fetch (e.g., [2015, 2016, ...]).
        force: If True, re-download even if cached.

    Returns:
        DataFrame with columns: fips, year, population
    """
    cache_path = _ensure_cache_dir() / "county_population.csv"

    if cache_path.exists() and not force:
        df = pd.read_csv(cache_path, dtype={"fips": str})
        # Check if we have all requested years
        cached_years = set(df["year"].unique())
        if set(years).issubset(cached_years):
            return df[df["year"].isin(years)]

    print("Downloading county population from Census Bureau...")
    all_data = []

    # Download 2010s file (covers 2010-2019)
    years_2010s = [y for y in years if 2010 <= y <= 2019]
    if years_2010s:
        print("  Fetching 2010-2019 estimates...")
        response = requests.get(CENSUS_POP_URLS["2010s"])
        response.raise_for_status()
        df_2010s = pd.read_csv(
            BytesIO(response.content),
            encoding="latin-1",
            dtype={"STATE": str, "COUNTY": str},
        )
        # Filter to county level (SUMLEV=050), not state totals
        df_2010s = df_2010s[df_2010s["SUMLEV"] == 50]
        df_2010s["fips"] = df_2010s["STATE"].str.zfill(2) + df_2010s["COUNTY"].str.zfill(3)

        # Melt population columns to long format
        pop_cols = [f"POPESTIMATE{y}" for y in years_2010s]
        df_long = df_2010s[["fips", "STNAME", "CTYNAME"] + pop_cols].melt(
            id_vars=["fips", "STNAME", "CTYNAME"],
            var_name="year_col",
            value_name="population",
        )
        df_long["year"] = df_long["year_col"].str.extract(r"(\d{4})").astype(int)
        df_long = df_long[df_long["year"].isin(years_2010s)]
        df_long["county_name"] = df_long["CTYNAME"] + ", " + df_long["STNAME"]
        all_data.append(df_long[["fips", "year", "population", "county_name"]])

    # Download 2020s file (covers 2020-2023)
    years_2020s = [y for y in years if 2020 <= y <= 2023]
    if years_2020s:
        print("  Fetching 2020-2023 estimates...")
        response = requests.get(CENSUS_POP_URLS["2020s"])
        response.raise_for_status()
        df_2020s = pd.read_csv(
            BytesIO(response.content),
            encoding="latin-1",
            dtype={"STATE": str, "COUNTY": str},
        )
        # Filter to county level (SUMLEV=050), not state totals
        df_2020s = df_2020s[df_2020s["SUMLEV"] == 50]
        df_2020s["fips"] = df_2020s["STATE"].str.zfill(2) + df_2020s["COUNTY"].str.zfill(3)

        # Melt population columns to long format
        pop_cols = [f"POPESTIMATE{y}" for y in years_2020s]
        df_long = df_2020s[["fips", "STNAME", "CTYNAME"] + pop_cols].melt(
            id_vars=["fips", "STNAME", "CTYNAME"],
            var_name="year_col",
            value_name="population",
        )
        df_long["year"] = df_long["year_col"].str.extract(r"(\d{4})").astype(int)
        df_long = df_long[df_long["year"].isin(years_2020s)]
        df_long["county_name"] = df_long["CTYNAME"] + ", " + df_long["STNAME"]
        all_data.append(df_long[["fips", "year", "population", "county_name"]])

    if not all_data:
        raise RuntimeError("Failed to download any population data")

    df = pd.concat(all_data, ignore_index=True)

    # Cache for future use
    df.to_csv(cache_path, index=False)
    print(f"Cached population data to {cache_path}")

    return df


def load_county_population(
    years: Optional[list[int]] = None,
    cache_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Load county population from cache.

    Args:
        years: Optional list of years to filter to.
        cache_path: Optional custom cache path.

    Returns:
        DataFrame with county population by year.

    Raises:
        FileNotFoundError: If population data hasn't been downloaded.
    """
    path = cache_path or (CACHE_DIR / "county_population.csv")
    if not path.exists():
        raise FileNotFoundError(
            f"Population data not found at {path}. "
            "Run download_county_population() first."
        )

    df = pd.read_csv(path, dtype={"fips": str})
    if years:
        df = df[df["year"].isin(years)]
    return df


def create_zip_to_fips_json(output_path: Path) -> None:
    """Create a simple ZIP-to-FIPS JSON lookup for the web layer.

    For ZIPs spanning multiple counties, uses the one with highest area_ratio.

    Args:
        output_path: Where to write the JSON file.
    """
    df = load_zip_to_fips()

    # For each ZIP, keep the county with highest area ratio
    df = df.sort_values("area_ratio", ascending=False)
    df = df.drop_duplicates(subset=["zip"], keep="first")

    # Create lookup dict
    lookup = {}
    for _, row in df.iterrows():
        lookup[row["zip"]] = {
            "fips": row["fips"],
            "county": row["county"],
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(lookup, f)

    print(f"Wrote ZIP-to-FIPS lookup ({len(lookup)} entries) to {output_path}")
