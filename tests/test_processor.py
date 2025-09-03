import pytest
import pandas as pd

from src.core.processor import (
    drop_columns,
    add_column,
    apply_transformation,
    filter_rows
)


# --- Fixtures ----------------------------------------------------------------

@pytest.fixture
def simple_df():
    """Reusable small DataFrame for transformation tests."""
    return pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})


# --- drop_columns tests ------------------------------------------------------

def test_drop_columns_when_column_exists(simple_df):
    """drop_columns should remove the specified column if it exists."""
    df2 = drop_columns(simple_df, ["a"])
    assert list(df2.columns) == ["b"]


def test_drop_columns_with_multiple_columns(simple_df):
    """drop_columns should drop multiple columns at once."""
    df2 = drop_columns(simple_df, ["a", "b"])
    assert df2.empty and df2.shape[1] == 0


def test_drop_columns_with_nonexistent_column(simple_df):
    """drop_columns should raise KeyError if a column does not exist."""
    with pytest.raises(KeyError):
        drop_columns(simple_df, ["nonexistent"])


# --- add_column tests --------------------------------------------------------

def test_add_column_with_valid_values(simple_df):
    """add_column should add a new column with given values."""
    df2 = add_column(simple_df, "c", [7, 8, 9])
    assert "c" in df2.columns
    assert df2.iloc[2]["c"] == 9


def test_add_column_with_wrong_length(simple_df):
    """add_column should raise ValueError if length of values != number of rows."""
    with pytest.raises(ValueError):
        add_column(simple_df, "c", [1, 2])


# --- apply_transformation tests ----------------------------------------------

def test_apply_transformation_with_lambda(simple_df):
    """apply_transformation should apply a lambda to a column correctly."""
    df2 = apply_transformation(simple_df, "a", lambda x: x * 2)
    assert df2["a"].tolist() == [2, 4, 6]


@pytest.mark.parametrize("func,expected", [
    (lambda x: x + 1, [2, 3, 4]),
    (lambda x: x ** 2, [1, 4, 9]),
])
def test_apply_transformation_with_various_functions(simple_df, func, expected):
    """apply_transformation should handle different transformation functions."""
    df2 = apply_transformation(simple_df, "a", func)
    assert df2["a"].tolist() == expected


def test_apply_transformation_with_nonexistent_column(simple_df):
    """apply_transformation should raise KeyError if column does not exist."""
    with pytest.raises(KeyError):
        apply_transformation(simple_df, "nonexistent", lambda x: x * 2)


# --- filter_rows tests -------------------------------------------------------

def test_filter_rows_with_numeric_condition(simple_df):
    """filter_rows should filter rows based on a numeric condition."""
    df2 = filter_rows(simple_df, lambda row: row["a"] > 1)
    assert df2["a"].tolist() == [2, 3]


def test_filter_rows_with_text_condition():
    """filter_rows should work on string values too."""
    df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie"]})
    df2 = filter_rows(df, lambda row: row["name"].startswith("A"))
    assert df2["name"].tolist() == ["Alice"]


def test_filter_rows_with_no_matches(simple_df):
    """filter_rows should return empty DataFrame if no rows match."""
    df2 = filter_rows(simple_df, lambda row: row["a"] > 100)
    assert df2.empty