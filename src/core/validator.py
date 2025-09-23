import pandas as pd
from typing import Dict, List, Optional


def check_missing_values(df: pd.DataFrame) -> Dict[str, int]:
    """Return a dictionary with counts of missing values per column."""
    raise NotImplementedError()


def validate_no_missing(df: pd.DataFrame, columns: Optional[List[str]] = None) -> bool:
    """Validate that specified columns contain no missing values."""
    raise NotImplementedError()


def validate_column_types(df: pd.DataFrame, expected_types: Dict[str, str]) -> bool:
    """Validate that columns have the expected pandas dtypes."""
    raise NotImplementedError()


def validate_unique(df: pd.DataFrame, columns: List[str]) -> bool:
    """Validate that specified columns contain only unique values."""
    raise NotImplementedError()


def validate_value_ranges(
    df: pd.DataFrame,
    column: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> bool:
    """Validate that column values lie within a given range."""
    raise NotImplementedError()


def validate_schema(df: pd.DataFrame, expected_columns: List[str]) -> bool:
    """Validate that DataFrame has exactly the expected columns (order ignored)."""
    raise NotImplementedError()