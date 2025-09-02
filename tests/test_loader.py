import pytest
import pandas as pd

from src.core.loader import (
    load_csv,
    preview_dataframe,
    get_dataframe_stat_summary,
    set_column_names,
    validate_csv_format
)


# Fixtures

@pytest.fixture
def simple_df():
    """A small reusable DataFrame for preview and summary tests."""
    return pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})


# load_csv tests

def test_load_csv_when_file_is_valid(tmp_path):
    """load_csv should correctly read a valid CSV file with default separator."""
    file = tmp_path / "test.csv"
    file.write_text("name,age\nAlice,30\nBob,25")

    df = load_csv(str(file))

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["name", "age"]
    assert df.iloc[0]["name"] == "Alice"


def test_load_csv_when_file_is_missing():
    """load_csv should raise FileNotFoundError if the file does not exist."""
    with pytest.raises(FileNotFoundError):
        load_csv("wrong.csv")


@pytest.mark.parametrize("sep,content", [
    (",", "name,age\nAlice,30"),
    (";", "name;age\nAlice;30"),
    ("|", "name|age\nAlice|30"),
])
def test_load_csv_with_various_separators(tmp_path, sep, content):
    """load_csv should handle different separators correctly."""
    file = tmp_path / "data.csv"
    file.write_text(content)

    df = load_csv(str(file), sep=sep)
    assert df.shape == (1, 2)


def test_load_csv_with_no_header(tmp_path):
    """load_csv should assign numeric column names if header=None is passed."""
    file = tmp_path / "test.csv"
    file.write_text("Alice,30\nBob,25")

    df = load_csv(str(file), header=None)
    assert list(df.columns) == [0, 1]


def test_load_csv_with_custom_na_values(tmp_path):
    """load_csv should interpret custom values as NaN when na_values is set."""
    file = tmp_path / "test.csv"
    file.write_text("name,score\nAlice,NA\nBob,missing")

    df = load_csv(str(file), na_values=["NA", "missing"])
    assert pd.isna(df.iloc[0]["score"])
    assert pd.isna(df.iloc[1]["score"])


def test_load_csv_with_utf16_encoding(tmp_path):
    """load_csv should correctly read a file encoded in UTF-16."""
    file = tmp_path / "test.csv"
    content = "name,age\nAlice,30\nBob,25"
    file.write_bytes(content.encode("utf-16"))

    df = load_csv(str(file), encoding="utf-16")
    assert df.shape == (2, 2)


def test_load_csv_with_empty_file(tmp_path):
    """load_csv should raise ValueError when the file is empty."""
    file = tmp_path / "empty.csv"
    file.write_text("")
    with pytest.raises(ValueError):
        load_csv(str(file))


def test_load_csv_with_invalid_encoding(tmp_path):
    """load_csv should raise UnicodeDecodeError if encoding is wrong."""
    file = tmp_path / "test.csv"
    content = "name,age\nAlice,30\nBob,25"
    # Save as utf-16
    file.write_bytes(content.encode("utf-16"))

    # Try to read as utf-8
    with pytest.raises(UnicodeDecodeError):
        load_csv(str(file), encoding="utf-8")


# preview_dataframe tests

def test_preview_dataframe_head(simple_df):
    """preview_dataframe should return the first N rows when tail=False."""
    preview = preview_dataframe(simple_df, row_number=2)
    assert preview.equals(simple_df.head(2))


def test_preview_dataframe_tail(simple_df):
    """preview_dataframe should return the last N rows when tail=True."""
    preview = preview_dataframe(simple_df, row_number=2, tail=True)
    assert preview.equals(simple_df.tail(2))


# get_dataframe_stat_summary tests

def test_get_dataframe_stat_summary_returns_expected_keys(simple_df):
    """get_dataframe_stat_summary should return dict with row/column count and missing values."""
    summary = get_dataframe_stat_summary(simple_df)
    assert isinstance(summary, dict)
    assert summary["row_count"] == 3
    assert summary["column_count"] == 2
    assert "missing_values" in summary


# set_column_names tests

def test_set_column_names_updates_columns():
    """set_column_names should replace DataFrame column names with provided list."""
    df = pd.DataFrame([[1, 2], [3, 4]])
    new_names = ["col1", "col2"]
    df2 = set_column_names(df, new_names)
    assert list(df2.columns) == new_names


# validate_csv_format tests

def test_validate_csv_format_when_file_is_correct(tmp_path):
    """validate_csv_format should return True for well-formed CSV with expected columns."""
    file = tmp_path / "valid.csv"
    file.write_text("col1,col2\n1,2\n3,4")
    assert validate_csv_format(str(file), expected_cols=2)


def test_validate_csv_format_when_columns_are_incorrect(tmp_path):
    """validate_csv_format should raise ValueError if column count is inconsistent."""
    file = tmp_path / "invalid.csv"
    file.write_text("col1,col2\n1,2,3")
    with pytest.raises(ValueError):
        validate_csv_format(str(file), expected_cols=2)
