import pandas as pd
from typing import List, Callable, Dict, Union


# --- Column operations -------------------------------------------------------

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


def create_column_from_existing(
    df: pd.DataFrame, 
    new_name: str, 
    func: Callable[[pd.Series], pd.Series]
) -> pd.DataFrame:
    """Create a new column based on existing ones using a function."""
    df[new_name] = func(df)
    return df


def apply_transformation(df: pd.DataFrame, column: str, func: Callable) -> pd.DataFrame:
    """Apply a transformation function to a column."""
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")
    df[column] = df[column].apply(func)
    return df


# --- Row operations ----------------------------------------------------------

def drop_rows_by_index(df: pd.DataFrame, indexes: List[int]) -> pd.DataFrame:
    """Drop rows by index."""
    return df.drop(index=indexes)


def drop_rows_by_condition(df: pd.DataFrame, condition: Callable) -> pd.DataFrame:
    """Drop rows that satisfy the given condition."""
    mask = df.apply(condition, axis=1)
    return df[~mask]


def filter_rows(df: pd.DataFrame, condition: Callable) -> pd.DataFrame:
    """Filter rows based on a condition function."""
    mask = df.apply(condition, axis=1)
    return df[mask]


# --- Data cleaning -----------------------------------------------------------

def drop_empty_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns that contain only NaN values."""
    return df.dropna(axis=1, how="all")


# --- Math and aggregation ----------------------------------------------------

def math_operation(df: pd.DataFrame, col1: str, col2: str, op: str, new_name: str) -> pd.DataFrame:
    """Perform math operation between two columns and store result in a new column.
    
    Supported ops: 'sum', 'diff', 'prod', 'mean'
    """
    if col1 not in df.columns or col2 not in df.columns:
        raise KeyError("One or both columns not found in DataFrame.")
    
    if op == "sum":
        df[new_name] = df[col1] + df[col2]
    elif op == "diff":
        df[new_name] = df[col1] - df[col2]
    elif op == "prod":
        df[new_name] = df[col1] * df[col2]
    elif op == "mean":
        df[new_name] = (df[col1] + df[col2]) / 2
    else:
        raise ValueError(f"Unsupported operation: {op}")
    
    return df


# --- Grouping and aggregation ------------------------------------------------

def group_and_aggregate(
    df: pd.DataFrame,
    by: Union[str, List[str]],
    agg_funcs: Dict[str, List[str]]
) -> pd.DataFrame:
    """Group DataFrame by one or more columns and apply aggregation functions.

    Example:
        group_and_aggregate(df, by="category", agg_funcs={"value": ["mean", "sum"]})
    """
    return df.groupby(by).agg(agg_funcs).reset_index()


# --- Text filtering ----------------------------------------------------------

def filter_text(df: pd.DataFrame, column: str, mode: str, pattern: str) -> pd.DataFrame:
    """Filter rows based on text matching in a column.

    Modes:
        - 'contains'
        - 'startswith'
        - 'endswith'
    """
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")

    if mode == "contains":
        mask = df[column].astype(str).str.contains(pattern, na=False)
    elif mode == "startswith":
        mask = df[column].astype(str).str.startswith(pattern, na=False)
    elif mode == "endswith":
        mask = df[column].astype(str).str.endswith(pattern, na=False)
    else:
        raise ValueError(f"Unsupported text filter mode: {mode}")

    return df[mask]
