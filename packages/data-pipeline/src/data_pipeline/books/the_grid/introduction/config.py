"""Configuration for The Grid: Introduction data pipeline."""

from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parents[7]  # Up to reading-data-companion/
BOOK_DATA_DIR = PROJECT_ROOT / "books" / "the-grid" / "data"
RAW_INTRO_DIR = BOOK_DATA_DIR / "raw" / "introduction"
RAW_DIR = RAW_INTRO_DIR / "Outage_Dataset"
PROCESSED_DIR = BOOK_DATA_DIR / "processed" / "introduction"

# Enrichment data files
BA_LOOKUP_FILE = RAW_INTRO_DIR / "BalancingAuthorityLookupTool.xlsx"
POWER_PROFILER_FILE = RAW_INTRO_DIR / "power_profiler_zipcode_tool_v14.3.xlsx"

# Years to include (exclude 2014 - only has Nov-Dec data)
YEARS = list(range(2015, 2024))  # 2015-2023

# Input file patterns
MERGED_FILE_PATTERN = "eaglei_outages_{year}_merged.csv"
WITH_EVENTS_FILE_PATTERN = "eaglei_outages_with_events_{year}.csv"

# Output files
OUTPUT_FILES = {
    "zip_to_fips": "zip_to_fips.json",
    "county_year_summary": "county_year_summary.json",
    "county_year_by_event": "county_year_by_event.json",
    "county_year_by_month": "county_year_by_month.json",
    "county_year_by_hour": "county_year_by_hour.json",
    "national_year_summary": "national_year_summary.json",
    "national_year_by_event": "national_year_by_event.json",
    "national_year_by_month": "national_year_by_month.json",
    "state_year_summary": "state_year_summary.json",
}

# Normalized event type categories
# Maps raw event type substrings to normalized categories
# Events can belong to multiple categories (one-hot encoding)
EVENT_CATEGORIES = [
    "severe_weather",
    "physical_attack",
    "vandalism",
    "theft",
    "suspicious_activity",
    "cyber_event",
    "fuel_supply",
    "transmission",
    "distribution",
    "substation",
    "generator",
    "system_operations",
    "sabotage",
    "other",
    "unknown",
]

# Mapping rules: substring patterns → categories
# Order matters for some patterns (more specific first)
EVENT_TYPE_PATTERNS = {
    # Weather-related (including "Natural Disaster" per Findings.md)
    "severe weather": ["severe_weather"],
    "weather": ["severe_weather"],
    "natural disaster": ["severe_weather"],  # Treat as weather per findings

    # Physical/security events
    "physical attack": ["physical_attack"],
    "actual physical attack": ["physical_attack"],
    "potential physical attack": ["physical_attack"],
    "threat of physical attack": ["physical_attack"],

    # Vandalism/theft/suspicious
    "vandalism": ["vandalism"],
    "theft": ["theft"],
    "suspicious activity": ["suspicious_activity"],
    "suspicious": ["suspicious_activity"],

    # Cyber
    "cyber": ["cyber_event"],

    # Infrastructure
    "transmission": ["transmission"],
    "distribution": ["distribution"],
    "substation": ["substation"],
    "switchyard": ["substation"],
    "generator": ["generator"],
    "fuel supply": ["fuel_supply"],
    "fuel": ["fuel_supply"],

    # Operations
    "system operations": ["system_operations"],
    "sabotage": ["sabotage"],

    # Catch-all
    "other": ["other"],
    "unknown": ["unknown"],
}


def get_raw_file(file_type: str, year: int) -> Path:
    """Get path to a raw data file."""
    if file_type == "merged":
        return RAW_DIR / MERGED_FILE_PATTERN.format(year=year)
    elif file_type == "with_events":
        return RAW_DIR / WITH_EVENTS_FILE_PATTERN.format(year=year)
    else:
        raise ValueError(f"Unknown file type: {file_type}")


def get_output_file(name: str) -> Path:
    """Get path to an output file."""
    if name not in OUTPUT_FILES:
        raise ValueError(f"Unknown output file: {name}")
    return PROCESSED_DIR / OUTPUT_FILES[name]
