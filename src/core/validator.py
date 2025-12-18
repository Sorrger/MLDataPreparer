import pandas as pd
from typing import Dict, List, Set, Any, Optional


def check_missing_values(df: pd.DataFrame) -> Dict[str, int]:
    """Return a dictionary with counts of missing values per column."""
    return df.isna().sum().to_dict()


def validate_no_missing(df: pd.DataFrame, columns: Optional[List[str]] = None) -> bool:
    """Validate that specified columns contain no missing values."""
    cols = columns or df.columns.tolist()
    missing = df[cols].isna().sum()
    if (missing > 0).any():
        raise ValueError(f"Missing values found in columns: {missing[missing > 0].to_dict()}")
    return True


def validate_column_types(df: pd.DataFrame, expected_types: Dict[str, str]) -> bool:
    """Validate that columns have the expected pandas dtypes."""
    mismatches = {}
    for col, expected in expected_types.items():
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not found in DataFrame.")
        if str(df[col].dtype) != expected:
            mismatches[col] = str(df[col].dtype)
    if mismatches:
        raise TypeError(f"Column dtype mismatches: {mismatches}")
    return True


def validate_unique(df: pd.DataFrame, columns: List[str]) -> bool:
    """Validate that specified columns contain only unique values."""
    if df.duplicated(subset=columns).any():
        raise ValueError(f"Duplicate values found in columns: {columns}")
    return True


def validate_value_ranges(
    df: pd.DataFrame,
    column: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> bool:
    """Validate that column values lie within a given range."""
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")
    if min_value is not None and (df[column] < min_value).any():
        raise ValueError(f"Values in column '{column}' are below {min_value}")
    if max_value is not None and (df[column] > max_value).any():
        raise ValueError(f"Values in column '{column}' are above {max_value}")
    return True


def validate_schema(df: pd.DataFrame, expected_columns: List[str]) -> bool:
    """Validate that DataFrame has exactly the expected columns (order ignored)."""
    if set(df.columns) != set(expected_columns):
        raise ValueError(
            f"Schema mismatch. Expected: {expected_columns}, Found: {list(df.columns)}"
        )
    return True

def validate_allowed_values(df: pd.DataFrame, column: str, allowed: Set[Any]) -> bool:
    """Validate that values in `column` are within allowed set."""
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")
    unique_vals = set(df[column].dropna().unique())
    bad = unique_vals - set(allowed)
    if bad:
        raise ValueError(f"Column '{column}' contains values outside allowed set: {sorted(bad)}")
    return True

def data_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    missing = df.isna().sum()
    missing_pct = (df.isna().mean() * 100).round(2)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing": missing.to_dict(),
        "missing_pct": missing_pct.to_dict(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "unique": df.nunique().to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "constant_columns": [
            c for c in df.columns if df[c].nunique() <= 1
        ],
    }

