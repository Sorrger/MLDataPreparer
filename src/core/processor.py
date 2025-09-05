import pandas as pd
from typing import List, Callable


def drop_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Drop specified columns from DataFrame."""
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise KeyError(f"Columns not found in DataFrame: {missing}")

    return df.drop(columns=columns)


def add_column(df: pd.DataFrame, name: str, values: List) -> pd.DataFrame:
    """Add a new column with provided values."""
    if len(values) != len(df):
        raise ValueError("Length of values does not match number of rows.")
    df[name] = values
    return df


def apply_transformation(df: pd.DataFrame, column: str, func: Callable) -> pd.DataFrame:
    """Apply a transformation function to a column."""
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")

    df[column] = df[column].apply(func)
    return df


def filter_rows(df: pd.DataFrame, condition: Callable) -> pd.DataFrame:
    """Filter rows based on a condition function."""
    mask = df.apply(condition, axis=1)
    return df[mask]