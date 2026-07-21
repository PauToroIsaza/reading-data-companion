"""Event type normalization for EAGLE-I outage data.

Normalizes 75+ raw event types to 15 categories.
Handles both old format (2014-2022) and new format (2023+).
"""

import re
from typing import Optional

import pandas as pd

from data_pipeline.books.the_grid.introduction.config import (
    EVENT_CATEGORIES,
    EVENT_TYPE_PATTERNS,
)


def normalize_event_type(raw_event: Optional[str]) -> list[str]:
    """Normalize a raw event type string to a list of categories.

    Args:
        raw_event: Raw event type string (e.g., "Severe Weather/Transmission Interruption"
                   or "- Physical attack - Vandalism").

    Returns:
        List of normalized category names (e.g., ["severe_weather", "transmission"]).
        Returns ["unknown"] if no patterns match.
    """
    if pd.isna(raw_event) or not raw_event:
        return ["unknown"]

    # Normalize: lowercase, strip whitespace
    event_lower = raw_event.lower().strip()

    # Handle 2023+ format: "- Category1 - Category2" → split on " - "
    if event_lower.startswith("-"):
        event_lower = event_lower.lstrip("- ")

    matched_categories = set()

    # Check each pattern
    for pattern, categories in EVENT_TYPE_PATTERNS.items():
        if pattern in event_lower:
            matched_categories.update(categories)

    # If nothing matched, mark as unknown
    if not matched_categories:
        return ["unknown"]

    # Return sorted for consistency
    return sorted(matched_categories)


def add_event_categories(df: pd.DataFrame, event_col: str = "Event Type") -> pd.DataFrame:
    """Add one-hot encoded event category columns to a DataFrame.

    Args:
        df: DataFrame with raw event types.
        event_col: Name of the column containing raw event types.

    Returns:
        DataFrame with additional boolean columns for each event category.
    """
    df = df.copy()

    # Normalize all event types
    df["_normalized_events"] = df[event_col].apply(normalize_event_type)

    # Create one-hot columns
    for category in EVENT_CATEGORIES:
        df[f"event_{category}"] = df["_normalized_events"].apply(
            lambda cats: category in cats
        )

    # Drop temporary column
    df = df.drop(columns=["_normalized_events"])

    return df


def get_primary_event_category(raw_event: Optional[str]) -> str:
    """Get the primary (first) event category for a raw event type.

    Useful when you need a single category rather than one-hot encoding.

    Args:
        raw_event: Raw event type string.

    Returns:
        Primary category name.
    """
    categories = normalize_event_type(raw_event)
    return categories[0] if categories else "unknown"


def summarize_event_categories(df: pd.DataFrame, event_col: str = "Event Type") -> pd.DataFrame:
    """Summarize the distribution of event categories in the data.

    Args:
        df: DataFrame with raw event types.
        event_col: Name of the column containing raw event types.

    Returns:
        DataFrame with category counts and percentages.
    """
    df_with_cats = add_event_categories(df, event_col)

    summary = []
    total_rows = len(df)

    for category in EVENT_CATEGORIES:
        col = f"event_{category}"
        count = df_with_cats[col].sum()
        pct = count / total_rows * 100 if total_rows > 0 else 0
        summary.append({
            "category": category,
            "count": count,
            "percentage": round(pct, 2),
        })

    return pd.DataFrame(summary).sort_values("count", ascending=False)


if __name__ == "__main__":
    # Test with sample event types
    test_events = [
        "Severe Weather",
        "Severe Weather/Transmission Interruption",
        "Natural Disaster",
        "- Physical attack - Vandalism - Suspicious activity",
        "Vandalism ",
        "Unknown",
        None,
        "Weather or natural disaster - Other",
        "Cyber Event",
    ]

    print("Event Type Normalization Test:")
    print("-" * 60)
    for event in test_events:
        normalized = normalize_event_type(event)
        print(f"{str(event):50} → {normalized}")
