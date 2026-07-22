"""Enrichment data for The Grid: Introduction.

Loads utility provider, market type, and eGRID subregion data,
then aggregates from ZIP level to FIPS (county) level.

Each FIPS gets:
- Primary value (most common across ZIPs in that county)
- List of all unique values
"""

import json
from collections import Counter

import pandas as pd

from data_pipeline.books.the_grid.introduction.config import (
    BA_LOOKUP_FILE,
    POWER_PROFILER_FILE,
    PROCESSED_DIR,
)

# Derived paths
ZIP_TO_FIPS_FILE = PROCESSED_DIR / "zip_to_fips.json"


def load_zip_to_fips() -> dict[str, str]:
    """Load ZIP to FIPS mapping.

    Returns:
        Dict mapping ZIP code (str) to FIPS code (str).
    """
    with open(ZIP_TO_FIPS_FILE) as f:
        data = json.load(f)
    # Extract just the fips from each entry
    return {zip_code: entry["fips"] for zip_code, entry in data.items()}


def load_ba_lookup() -> pd.DataFrame:
    """Load Balancing Authority lookup data.

    Returns:
        DataFrame with columns: zip, utility_provider, market_type, balancing_authority
    """
    df = pd.read_excel(
        BA_LOOKUP_FILE,
        sheet_name="I. BA Lookup Table",
        usecols=["ZIP code", "Market Type", "New Utility_Name ", "Balancing Authority"],
    )

    # Rename columns
    df = df.rename(columns={
        "ZIP code": "zip",
        "Market Type": "market_type",
        "New Utility_Name ": "utility_provider",
        "Balancing Authority": "balancing_authority",
    })

    # Normalize ZIP to 5-digit string
    df["zip"] = df["zip"].astype(str).str.zfill(5)

    # Clean string columns
    for col in ["utility_provider", "market_type", "balancing_authority"]:
        df[col] = df[col].fillna("").str.strip()

    return df


def load_egrid_subregions() -> pd.DataFrame:
    """Load eGRID subregion lookup data.

    Returns:
        DataFrame with columns: zip, egrid_subregions (list of subregions per ZIP)
    """
    df = pd.read_excel(
        POWER_PROFILER_FILE,
        sheet_name="Zip-subregion",
    )

    # Normalize ZIP to 5-digit string
    df["zip"] = df["zip"].astype(str).str.zfill(5)

    # Combine subregion columns into a list (filtering out NaN)
    def combine_subregions(row):
        subs = []
        for col in ["Subregion 1", "Subregion 2", "Subregion 3"]:
            if pd.notna(row[col]):
                subs.append(row[col])
        return subs

    df["egrid_subregions"] = df.apply(combine_subregions, axis=1)

    # Primary subregion is always Subregion 1
    df["egrid_subregion_primary"] = df["Subregion 1"]

    return df[["zip", "egrid_subregion_primary", "egrid_subregions"]]


def get_primary_and_list(values: list) -> tuple[str, list[str]]:
    """Get the most common value and list of unique values.

    Args:
        values: List of values (may contain empty strings or NaN)

    Returns:
        Tuple of (primary_value, unique_values_list)
    """
    # Filter out empty strings, None, and NaN values
    filtered = [
        str(v) for v in values
        if v and not (isinstance(v, float) and pd.isna(v))
    ]
    # Also filter out empty strings after conversion
    filtered = [v for v in filtered if v.strip()]

    if not filtered:
        return "", []

    # Count occurrences
    counts = Counter(filtered)
    primary = counts.most_common(1)[0][0]
    unique_list = sorted(set(filtered))

    return primary, unique_list


def aggregate_to_fips(zip_data: pd.DataFrame, zip_to_fips: dict[str, str]) -> pd.DataFrame:
    """Aggregate ZIP-level data to FIPS level.

    Args:
        zip_data: DataFrame with 'zip' column and enrichment columns
        zip_to_fips: Mapping from ZIP to FIPS

    Returns:
        DataFrame indexed by FIPS with primary + list columns for each enrichment
    """
    # Add FIPS column
    zip_data = zip_data.copy()
    zip_data["fips"] = zip_data["zip"].map(zip_to_fips)

    # Drop ZIPs without FIPS mapping
    zip_data = zip_data.dropna(subset=["fips"])

    # Columns to aggregate (excluding zip and fips)
    # Handle egrid_subregions specially since it's already a list

    records = []

    for fips, group in zip_data.groupby("fips"):
        record = {"fips": fips}

        # Aggregate utility_provider
        if "utility_provider" in group.columns:
            primary, all_values = get_primary_and_list(group["utility_provider"].tolist())
            record["utility_provider"] = primary
            record["utility_providers_all"] = all_values

        # Aggregate market_type
        if "market_type" in group.columns:
            primary, all_values = get_primary_and_list(group["market_type"].tolist())
            record["market_type"] = primary
            record["market_types_all"] = all_values

        # Aggregate balancing_authority
        if "balancing_authority" in group.columns:
            primary, all_values = get_primary_and_list(group["balancing_authority"].tolist())
            record["balancing_authority"] = primary
            record["balancing_authorities_all"] = all_values

        # Aggregate eGRID subregions
        if "egrid_subregion_primary" in group.columns:
            # For primary, use most common primary subregion
            primaries = group["egrid_subregion_primary"].dropna().tolist()
            primary, _ = get_primary_and_list(primaries)
            record["egrid_subregion"] = primary

            # For all, flatten all subregion lists
            all_subs = []
            for subs in group["egrid_subregions"]:
                all_subs.extend(subs)
            record["egrid_subregions_all"] = sorted(set(all_subs))

        records.append(record)

    return pd.DataFrame(records)


def build_fips_enrichments() -> pd.DataFrame:
    """Build complete FIPS-level enrichment data.

    Returns:
        DataFrame with FIPS as index and enrichment columns.
    """
    print("Loading ZIP to FIPS mapping...")
    zip_to_fips = load_zip_to_fips()
    print(f"  {len(zip_to_fips):,} ZIP codes mapped")

    print("Loading Balancing Authority data...")
    ba_data = load_ba_lookup()
    print(f"  {len(ba_data):,} ZIP records")

    print("Loading eGRID subregion data...")
    egrid_data = load_egrid_subregions()
    print(f"  {len(egrid_data):,} ZIP records")

    # Merge BA and eGRID data on ZIP
    print("Merging ZIP-level data...")
    zip_data = ba_data.merge(egrid_data, on="zip", how="outer")
    print(f"  {len(zip_data):,} combined ZIP records")

    # Aggregate to FIPS
    print("Aggregating to FIPS level...")
    fips_data = aggregate_to_fips(zip_data, zip_to_fips)
    print(f"  {len(fips_data):,} FIPS records")

    return fips_data


def load_fips_enrichments() -> pd.DataFrame:
    """Load FIPS enrichments for use in build_dataset.

    This is the main entry point for the build_dataset module.

    Returns:
        DataFrame with columns:
        - fips: FIPS code
        - utility_provider: Primary utility provider
        - utility_providers_all: List of all utility providers
        - market_type: Primary market type
        - market_types_all: List of all market types
        - balancing_authority: Primary balancing authority
        - balancing_authorities_all: List of all balancing authorities
        - egrid_subregion: Primary eGRID subregion
        - egrid_subregions_all: List of all eGRID subregions
    """
    return build_fips_enrichments()


if __name__ == "__main__":
    # Test the enrichment pipeline
    df = build_fips_enrichments()
    print("\nSample output:")
    print(df.head(10).to_string())

    print("\nColumn info:")
    for col in df.columns:
        print(f"  {col}: {df[col].dtype}")
