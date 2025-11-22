import pytest
import pandas as pd
from datetime import datetime, timedelta

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
    resample_time_series,
    rolling_stat,
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

def test_drop_rows_by_condition(simple_df):
    df2 = drop_rows_by_condition(simple_df, lambda row: row["b"] > 4)
    assert df2["b"].tolist() == [4]


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

def test_apply_transformation(simple_df):
    df2 = apply_transformation(simple_df, "a", lambda x: x * 10)
    assert df2["a"].tolist() == [10, 20, 30]
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


def test_group_and_aggregate_multiple_metrics(group_df):
    result = group_and_aggregate(
        group_df,
        by="category",
        agg_funcs={"value": ["sum", "mean", "max"]}
    )
    assert "sum" in result["value"].columns
    assert "mean" in result["value"].columns
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

def test_resample_time_series_daily_to_weekly():
    dates = pd.date_range(start="2023-01-01", periods=7, freq="D")
    df = pd.DataFrame({
        "ts": dates,
        "value": [1,2,3,4,5,6,7]
    })
    res = resample_time_series(df, "ts", "W", {"value": "sum"})
    # weekly sum of 7 days should be 28
    assert res["value"].iloc[0] == sum(range(1,8))

def test_rolling_stat_mean(simple_df):
    # use column 'a' = [1,2,3]
    series = rolling_stat(simple_df, "a", window=2, func="mean")
    # first valid value at index 1 should be (1+2)/2 = 1.5
    assert pytest.approx(series.iloc[1]) == 1.5


def test_filter_rows(simple_df):
    df2 = filter_rows(simple_df, lambda row: row["a"] > 1)
    assert df2["a"].tolist() == [2, 3]

def test_resample_time_series_multi_agg():
    """resample_time_series multi-column aggregation"""
    dates = pd.date_range("2023-01-01", periods=4, freq="D")
    df = pd.DataFrame({
        "ts": dates,
        "v1": [1, 2, 3, 4],
        "v2": [10, 20, 30, 40]
    })

    res = resample_time_series(
        df,
        "ts",
        "W",
        {"v1": "sum", "v2": "mean"}
    )

    assert res.shape[0] == 1
    assert res["v1"].iloc[0] == 10
    assert res["v2"].iloc[0] == 25

def test_rolling_stat_std(simple_df):
    """rolling_stat std"""
    series = rolling_stat(simple_df, "a", window=2, func="std")
    assert series.iloc[1] == pytest.approx(0.7071, rel=1e-2)

def test_filter_text_endswith():
    """filter_text endswith"""
    df = pd.DataFrame({"city": ["Berlin", "Paris", "Turin"]})
    result = filter_text(df, "city", "endswith", "in")
    assert result["city"].tolist() == ["Berlin", "Turin"]
