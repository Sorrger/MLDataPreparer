import pandas as pd
from typing import List, Callable


def drop_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Drop specified columns from DataFrame."""
    raise NotImplementedError()


def add_column(df: pd.DataFrame, name: str, values: List) -> pd.DataFrame:
    """Add a new column with provided values."""
    raise NotImplementedError()


def apply_transformation(df: pd.DataFrame, column: str, func: Callable) -> pd.DataFrame:
    """Apply a transformation function to a column."""
    raise NotImplementedError()


def filter_rows(df: pd.DataFrame, condition: Callable) -> pd.DataFrame:
    """Filter rows based on a condition function."""
    raise NotImplementedError()