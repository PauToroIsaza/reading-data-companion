"""File I/O utilities for data pipelines."""

import json
from pathlib import Path
from typing import Any

import pandas as pd


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Read a CSV file into a DataFrame.

    Args:
        path: Path to the CSV file.
        **kwargs: Additional arguments passed to pd.read_csv.

    Returns:
        DataFrame with the CSV contents.
    """
    return pd.read_csv(path, **kwargs)


def write_json(data: Any, path: Path, indent: int = 2) -> None:
    """Write data to a JSON file.

    Args:
        data: Data to write (must be JSON-serializable).
        path: Output path.
        indent: JSON indentation level.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)


def load_json(path: Path) -> Any:
    """Load data from a JSON file.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON data.
    """
    with open(path) as f:
        return json.load(f)


def dataframe_to_json_records(df: pd.DataFrame, path: Path) -> None:
    """Write a DataFrame to JSON as a list of records.

    Args:
        df: DataFrame to write.
        path: Output path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    # Convert to records and handle NaN/Infinity
    records = df.to_dict(orient="records")
    write_json(records, path)
