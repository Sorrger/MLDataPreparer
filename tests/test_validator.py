import pytest
import pandas as pd
from src.core import validator


# --- Fixtures ----------------------------------------------------------------

@pytest.fixture
def valid_df():
    """A clean DataFrame with no missing values."""
    return pd.DataFrame({
        "id": [1, 2, 3],
        "age": [25, 30, 40],
        "name": ["Alice", "Bob", "Charlie"]
    })


@pytest.fixture
def df_with_missing():
    """DataFrame containing missing values."""
    return pd.DataFrame({
        "id": [1, None, 3],
        "age": [25, None, 40],
        "name": ["Alice", None, "Charlie"]
    })


# --- check_missing_values tests ----------------------------------------------

def test_check_missing_values_counts(df_with_missing):
    """check_missing_values should return correct counts of NaN per column."""
    result = validator.check_missing_values(df_with_missing)
    assert result["id"] == 1
    assert result["age"] == 1
    assert result["name"] == 1


# --- validate_no_missing tests ------------------------------------------------

def test_validate_no_missing_passes(valid_df):
    """validate_no_missing should return True if no missing values."""
    assert validator.validate_no_missing(valid_df)


def test_validate_no_missing_raises(df_with_missing):
    """validate_no_missing should raise ValueError if missing values exist."""
    with pytest.raises(ValueError):
        validator.validate_no_missing(df_with_missing)

def test_validate_no_missing_subset(valid_df):
    """validate_no_missing passes when selecting subset"""
    assert validator.validate_no_missing(valid_df, ["id"])


# --- validate_column_types tests ---------------------------------------------

def test_validate_column_types_with_correct_types(valid_df):
    """validate_column_types should pass when dtypes match expected."""
    expected_types = {"id": "int64", "age": "int64", "name": "object"}
    assert validator.validate_column_types(valid_df, expected_types)

def test_validate_column_types_with_mismatch(valid_df):
    """validate_column_types should raise TypeError if dtype mismatches."""
    expected_types = {"id": "float64"}  # wrong type
    with pytest.raises(TypeError):
        validator.validate_column_types(valid_df, expected_types)

def test_validate_column_types_missing_column(valid_df):
    """validate_column_types missing column"""
    with pytest.raises(KeyError):
        validator.validate_column_types(valid_df, {"missing": "int64"})

# --- validate_unique tests ---------------------------------------------------

def test_validate_unique_passes(valid_df):
    """validate_unique should pass when all values are unique."""
    assert validator.validate_unique(valid_df, ["id"])


def test_validate_unique_raises():
    """validate_unique should raise ValueError if duplicates exist."""
    df = pd.DataFrame({"id": [1, 1, 2]})
    with pytest.raises(ValueError):
        validator.validate_unique(df, ["id"])


# --- validate_value_ranges tests ---------------------------------------------

def test_validate_value_ranges_within_bounds(valid_df):
    """validate_value_ranges should pass when values are within given range."""
    assert validator.validate_value_ranges(valid_df, "age", min_value=20, max_value=50)


def test_validate_value_ranges_below_min(valid_df):
    """validate_value_ranges should raise ValueError when values < min_value."""
    with pytest.raises(ValueError):
        validator.validate_value_ranges(valid_df, "age", min_value=30)


def test_validate_value_ranges_above_max(valid_df):
    """validate_value_ranges should raise ValueError when values > max_value."""
    with pytest.raises(ValueError):
        validator.validate_value_ranges(valid_df, "age", max_value=35)


# --- validate_schema tests ---------------------------------------------------

def test_validate_schema_passes(valid_df):
    """validate_schema should pass when columns match expected set."""
    assert validator.validate_schema(valid_df, ["id", "age", "name"])


def test_validate_schema_raises(valid_df):
    """validate_schema should raise ValueError when schema differs."""
    with pytest.raises(ValueError):
        validator.validate_schema(valid_df, ["id", "age"])

def test_validate_allowed_values_passes(valid_df):
    """validate_no_missing passes when selecting subset"""
    assert validator.validate_allowed_values(valid_df, "name", {"Alice", "Bob", "Charlie"})

def test_validate_allowed_values_raises(valid_df):
    """"""
    with pytest.raises(ValueError):
        validator.validate_allowed_values(valid_df, "name", {"Alice", "Bob"})

def test_validate_unique_multiple_columns():
    """validate_unique multiple columns"""
    df = pd.DataFrame({"id": [1, 2, 1], "code": [5, 5, 5]})
    with pytest.raises(ValueError):
        validator.validate_unique(df, ["id", "code"])

def test_validate_value_ranges_upper_only(valid_df):
    """validate_value_ranges only max bound"""
    with pytest.raises(ValueError):
        validator.validate_value_ranges(valid_df, "age", max_value=20)

def test_validate_allowed_values_bad(valid_df):
    """validate_allowed_values with unexpected values"""
    with pytest.raises(ValueError):
        validator.validate_allowed_values(valid_df, "name", {"Alice"})
