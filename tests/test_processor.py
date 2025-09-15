import pytest
import pandas as pd

from src.core.processor import (
    drop_columns,
    add_column,
    apply_transformation,
    filter_rows,
    create_column_from_existing,
    drop_rows_by_index,
    drop_rows_by_condition,
    drop_empty_columns,
    math_operation,
    group_and_aggregate,
    filter_text,
)


# --- Fixtures ----------------------------------------------------------------

@pytest.fixture
def simple_df():
    """Reusable small DataFrame for transformation tests."""
    return pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})


@pytest.fixture
def df_with_missing():
    """DataFrame with NaN values for cleaning tests."""
    return pd.DataFrame({"x": [1, None, 3], "y": [None, None, None]})


@pytest.fixture
def group_df():
    """DataFrame for group and aggregate tests."""
    return pd.DataFrame({
        "category": ["A", "A", "B", "B"],
        "value": [10, 20, 30, 40]
    })


# --- create_column_from_existing tests ---------------------------------------

def test_create_column_from_existing_with_sum(simple_df):
    """create_column_from_existing should create a new column using a function."""
    df2 = create_column_from_existing(simple_df, "sum_ab", lambda df: df["a"] + df["b"])
    assert "sum_ab" in df2.columns
    assert df2["sum_ab"].tolist() == [5, 7, 9]


# --- drop_rows_by_index tests ------------------------------------------------

def test_drop_rows_by_index_removes_rows(simple_df):
    """drop_rows_by_index should remove rows at given indices."""
    df2 = drop_rows_by_index(simple_df, [0, 2])
    assert df2["a"].tolist() == [2]


# --- drop_rows_by_condition tests --------------------------------------------

def test_drop_rows_by_condition_removes_matching(simple_df):
    """drop_rows_by_condition should drop rows where condition is True."""
    df2 = drop_rows_by_condition(simple_df, lambda row: row["a"] < 3)
    assert df2["a"].tolist() == [3]


# --- drop_empty_columns tests ------------------------------------------------

def test_drop_empty_columns_removes_all_nan_columns(df_with_missing):
    """drop_empty_columns should drop columns that contain only NaN values."""
    df2 = drop_empty_columns(df_with_missing)
    assert "y" not in df2.columns
    assert "x" in df2.columns


# --- math_operation tests ----------------------------------------------------

@pytest.mark.parametrize("op,expected", [
    ("sum", [5, 7, 9]),
    ("diff", [-3, -3, -3]),
    ("prod", [4, 10, 18]),
    ("mean", [2.5, 3.5, 4.5]),
])
def test_math_operation_valid_ops(simple_df, op, expected):
    """math_operation should correctly compute sum, diff, prod, and mean."""
    df2 = math_operation(simple_df, "a", "b", op, "result")
    assert df2["result"].tolist() == expected


def test_math_operation_with_invalid_op(simple_df):
    """math_operation should raise ValueError if operation is not supported."""
    with pytest.raises(ValueError):
        math_operation(simple_df, "a", "b", "invalid", "result")


def test_math_operation_with_missing_column(simple_df):
    """math_operation should raise KeyError if column does not exist."""
    with pytest.raises(KeyError):
        math_operation(simple_df, "a", "nonexistent", "sum", "result")


# --- group_and_aggregate tests -----------------------------------------------

def test_group_and_aggregate_with_single_function(group_df):
    """group_and_aggregate should aggregate values by group with single metric."""
    result = group_and_aggregate(group_df, by="category", agg_funcs={"value": ["mean"]})
    assert result.shape[0] == 2
    assert "mean" in result["value"].columns


def test_group_and_aggregate_with_multiple_functions(group_df):
    """group_and_aggregate should support multiple aggregation functions."""
    result = group_and_aggregate(group_df, by="category", agg_funcs={"value": ["sum", "max"]})
    assert "sum" in result["value"].columns
    assert "max" in result["value"].columns


# --- filter_text tests -------------------------------------------------------

def test_filter_text_with_contains():
    """filter_text should return rows where column contains substring."""
    df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})
    result = filter_text(df, "name", "contains", "li")
    assert result["name"].tolist() == ["Alice", "Charlie"]


def test_filter_text_with_startswith():
    """filter_text should return rows where column starts with prefix."""
    df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})
    result = filter_text(df, "name", "startswith", "A")
    assert result["name"].tolist() == ["Alice"]


def test_filter_text_with_invalid_mode(simple_df):
    """filter_text should raise ValueError if mode is not supported."""
    with pytest.raises(ValueError):
        filter_text(simple_df, "a", "invalid", "1")