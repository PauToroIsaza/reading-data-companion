"""Build the final dataset JSONs for The Grid: Introduction visualization.

Processes EAGLE-I outage data to produce:
- county_year_summary.json
- county_year_by_event.json
- county_year_by_month.json
- county_year_by_hour.json
- national_year_summary.json
- national_year_by_event.json
- national_year_by_month.json
- state_year_summary.json
"""

import pandas as pd

from data_pipeline.common.io import read_csv, dataframe_to_json_records
from data_pipeline.common.lookups import load_county_population
from data_pipeline.books.the_grid.introduction.config import (
    YEARS,
    EVENT_CATEGORIES,
    get_raw_file,
    get_output_file,
)
from data_pipeline.books.the_grid.introduction.normalize_events import (
    add_event_categories,
    get_primary_event_category,
)


def load_all_years() -> pd.DataFrame:
    """Load and concatenate with_events files for all years."""
    dfs = []

    for year in YEARS:
        path = get_raw_file("with_events", year)
        print(f"Loading {path.name}...")

        df = read_csv(path)
        df["year"] = year

        # Ensure fips is string with leading zeros
        df["fips"] = df["fips"].astype(str).str.zfill(5)

        # Parse start_time to extract month and hour
        df["start_time"] = pd.to_datetime(df["start_time"])
        df["month"] = df["start_time"].dt.month
        df["hour"] = df["start_time"].dt.hour

        # Compute customer_hours for each outage
        df["customer_hours"] = df["duration"] * df["mean_customers"]

        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


def build_county_year_summary(df: pd.DataFrame, population: pd.DataFrame) -> pd.DataFrame:
    """Build county-year summary with totals and per-capita metrics."""
    agg = df.groupby(["fips", "state", "county", "year"]).agg(
        customer_hours=("customer_hours", "sum"),
        outage_count=("customer_hours", "count"),
    ).reset_index()

    # Join with population
    agg = agg.merge(
        population[["fips", "year", "population"]],
        on=["fips", "year"],
        how="left",
    )

    # Compute per-capita metric
    agg["customer_hours_per_capita"] = (
        agg["customer_hours"] / agg["population"]
    ).round(6)

    return agg


def build_county_year_by_event(df: pd.DataFrame) -> pd.DataFrame:
    """Build county-year breakdown by event type with duration stats."""
    # Add event category columns
    df = add_event_categories(df, "Event Type")

    records = []

    for (fips, year), group in df.groupby(["fips", "year"]):
        for category in EVENT_CATEGORIES:
            col = f"event_{category}"
            subset = group[group[col]]

            if len(subset) == 0:
                continue

            records.append({
                "fips": fips,
                "year": year,
                "event_type": category,
                "customer_hours": subset["customer_hours"].sum(),
                "outage_count": len(subset),
                "duration_min_hours": subset["duration"].min(),
                "duration_max_hours": subset["duration"].max(),
                "duration_avg_hours": subset["duration"].mean(),
            })

    result = pd.DataFrame(records)

    # Round duration stats
    for col in ["duration_min_hours", "duration_max_hours", "duration_avg_hours"]:
        if col in result.columns:
            result[col] = result[col].round(2)

    result["customer_hours"] = result["customer_hours"].round(2)

    return result


def build_county_year_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Build county-year breakdown by month."""
    agg = df.groupby(["fips", "year", "month"]).agg(
        customer_hours=("customer_hours", "sum"),
        outage_count=("customer_hours", "count"),
    ).reset_index()

    agg["customer_hours"] = agg["customer_hours"].round(2)

    return agg


def build_county_year_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    """Build county-year breakdown by hour of day."""
    agg = df.groupby(["fips", "year", "hour"]).agg(
        customer_hours=("customer_hours", "sum"),
        outage_count=("customer_hours", "count"),
    ).reset_index()

    agg["customer_hours"] = agg["customer_hours"].round(2)

    return agg


def build_national_year_summary(county_summary: pd.DataFrame) -> pd.DataFrame:
    """Build national-level yearly summary."""
    agg = county_summary.groupby("year").agg(
        customer_hours=("customer_hours", "sum"),
        outage_count=("outage_count", "sum"),
        counties_affected=("fips", "nunique"),
        states_affected=("state", "nunique"),
        total_population=("population", "sum"),
    ).reset_index()

    agg["customer_hours"] = agg["customer_hours"].round(2)

    return agg


def build_national_year_by_event(county_by_event: pd.DataFrame) -> pd.DataFrame:
    """Build national-level yearly breakdown by event type."""
    agg = county_by_event.groupby(["year", "event_type"]).agg(
        customer_hours=("customer_hours", "sum"),
        outage_count=("outage_count", "sum"),
    ).reset_index()

    agg["customer_hours"] = agg["customer_hours"].round(2)

    return agg


def build_national_year_by_month(county_by_month: pd.DataFrame) -> pd.DataFrame:
    """Build national-level yearly breakdown by month."""
    agg = county_by_month.groupby(["year", "month"]).agg(
        customer_hours=("customer_hours", "sum"),
        outage_count=("outage_count", "sum"),
    ).reset_index()

    agg["customer_hours"] = agg["customer_hours"].round(2)

    return agg


def build_state_year_summary(county_summary: pd.DataFrame) -> pd.DataFrame:
    """Build state-level yearly summary."""
    agg = county_summary.groupby(["state", "year"]).agg(
        customer_hours=("customer_hours", "sum"),
        outage_count=("outage_count", "sum"),
        counties_affected=("fips", "nunique"),
        total_population=("population", "sum"),
    ).reset_index()

    agg["customer_hours_per_capita"] = (
        agg["customer_hours"] / agg["total_population"]
    ).round(6)

    agg["customer_hours"] = agg["customer_hours"].round(2)

    return agg


def build_all() -> dict[str, pd.DataFrame]:
    """Build all datasets and return them as a dictionary."""
    print("=" * 60)
    print("Building The Grid: Introduction datasets")
    print("=" * 60)

    # Load raw data
    print("\n1. Loading raw data...")
    df = load_all_years()
    print(f"   Loaded {len(df):,} outage records across {len(YEARS)} years")

    # Load population data
    print("\n2. Loading population data...")
    population = load_county_population(years=YEARS)
    print(f"   Loaded population for {len(population):,} county-years")

    # Build datasets
    print("\n3. Building county-year summary...")
    county_summary = build_county_year_summary(df, population)
    print(f"   {len(county_summary):,} county-year records")

    print("\n4. Building county-year by event type...")
    county_by_event = build_county_year_by_event(df)
    print(f"   {len(county_by_event):,} records")

    print("\n5. Building county-year by month...")
    county_by_month = build_county_year_by_month(df)
    print(f"   {len(county_by_month):,} records")

    print("\n6. Building county-year by hour...")
    county_by_hour = build_county_year_by_hour(df)
    print(f"   {len(county_by_hour):,} records")

    print("\n7. Building national summaries...")
    national_summary = build_national_year_summary(county_summary)
    national_by_event = build_national_year_by_event(county_by_event)
    national_by_month = build_national_year_by_month(county_by_month)
    print(f"   National summary: {len(national_summary)} years")

    print("\n8. Building state summaries...")
    state_summary = build_state_year_summary(county_summary)
    print(f"   {len(state_summary):,} state-year records")

    return {
        "county_year_summary": county_summary,
        "county_year_by_event": county_by_event,
        "county_year_by_month": county_by_month,
        "county_year_by_hour": county_by_hour,
        "national_year_summary": national_summary,
        "national_year_by_event": national_by_event,
        "national_year_by_month": national_by_month,
        "state_year_summary": state_summary,
    }


def write_all(datasets: dict[str, pd.DataFrame]) -> None:
    """Write all datasets to JSON files."""
    print("\n9. Writing JSON files...")

    for name, df in datasets.items():
        path = get_output_file(name)
        dataframe_to_json_records(df, path)
        print(f"   Wrote {path.name} ({len(df):,} records)")

    print("\nDone!")


if __name__ == "__main__":
    datasets = build_all()
    write_all(datasets)
