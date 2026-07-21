"""Orchestrator for The Grid: Introduction data pipeline.

Runs all pipeline steps in order:
1. Download lookup data (ZIP-to-FIPS, county population)
2. Build and write all output datasets

Usage:
    python -m data_pipeline.books.the_grid.introduction.run [--force]

Options:
    --force     Re-download lookup data even if cached
"""

import argparse
import sys

from data_pipeline.common.lookups import (
    download_zip_to_fips,
    download_county_population,
    create_zip_to_fips_json,
)
from data_pipeline.books.the_grid.introduction.config import (
    YEARS,
    get_output_file,
)
from data_pipeline.books.the_grid.introduction.build_dataset import (
    build_all,
    write_all,
)


def run_pipeline(force_download: bool = False) -> None:
    """Run the full pipeline.

    Args:
        force_download: If True, re-download lookup data even if cached.
    """
    print("=" * 60)
    print("The Grid: Introduction - Data Pipeline")
    print("=" * 60)

    # Step 1: Download lookup data
    print("\n[Step 1/3] Downloading lookup data...")
    print("-" * 40)

    print("\nZIP-to-FIPS crosswalk:")
    download_zip_to_fips(force=force_download)

    print("\nCounty population (ACS):")
    download_county_population(years=YEARS, force=force_download)

    # Step 2: Create ZIP-to-FIPS JSON for web layer
    print("\n[Step 2/3] Creating ZIP-to-FIPS lookup JSON...")
    print("-" * 40)
    create_zip_to_fips_json(get_output_file("zip_to_fips"))

    # Step 3: Build all datasets
    print("\n[Step 3/3] Building datasets...")
    print("-" * 40)
    datasets = build_all()
    write_all(datasets)

    print("\n" + "=" * 60)
    print("Pipeline complete!")
    print("=" * 60)
    print(f"\nOutput files written to:")
    print(f"  {get_output_file('county_year_summary').parent}")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run The Grid: Introduction data pipeline"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download lookup data even if cached",
    )
    args = parser.parse_args()

    try:
        run_pipeline(force_download=args.force)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
