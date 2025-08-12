import pytest
import pandas as pd

from src.core.loader import (
    load_csv,
    preview_dataframe,
    get_dataframe_stat_summary,
    set_column_names,
    validate_csv_format
)


def test_load_csv_valid_file(tmp_path):
    file = tmp_path / "test.csv"
    file.write_text("name,age\nAlice,30\nBob,25")

    df = load_csv(str(file))

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ["name", "age"]
    assert df.iloc[0]["name"] == "Alice"


def test_load_csv_missing_file():
    with pytest.raises(FileNotFoundError):
        load_csv("wrong.csv")


def test_load_csv_invalid_separator(tmp_path):
    file = tmp_path / "test.csv"
    file.write_text("name;age\nAlice;30")

    df = load_csv(str(file), sep=",")
    assert df.shape[1] == 1


def test_load_csv_no_header(tmp_path):
    file = tmp_path / "test.csv"
    file.write_text("Alice,30\nBob,25")

    df = load_csv(str(file), header=None)
    assert list(df.columns) == [0, 1]


def test_load_csv_custom_na_values(tmp_path):
    file = tmp_path / "test.csv"
    file.write_text("name,score\nAlice,NA\nBob,missing")

    df = load_csv(str(file), na_values=["NA", "missing"])
    assert pd.isna(df.iloc[0]["score"])
    assert pd.isna(df.iloc[1]["score"])


def test_load_csv_encoding_utf16(tmp_path):
    file = tmp_path / "test.csv"
    content = "name,age\nAlice,30\nBob,25"
    file.write_bytes(content.encode("utf-16"))

    df = load_csv(str(file), encoding="utf-16")
    assert df.shape == (2, 2)


def test_preview_dataframe_head():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    preview = preview_dataframe(df, row_number=2)
    assert preview.equals(df.head(2))


def test_preview_dataframe_tail():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    preview = preview_dataframe(df, row_number=2, tail=True)
    assert preview.equals(df.tail(2))


def test_get_dataframe_stat_summary():
    df = pd.DataFrame({
        "a": [1, 2, 3],
        "b": [None, 5, 6]
    })
    summary = get_dataframe_stat_summary(df)
    assert isinstance(summary, dict)
    assert summary["row_count"] == 3
    assert summary["column_count"] == 2
    assert "missing_values" in summary


def test_set_column_names():
    df = pd.DataFrame([[1, 2], [3, 4]])
    new_names = ["col1", "col2"]
    df2 = set_column_names(df, new_names)
    assert list(df2.columns) == new_names


def test_validate_csv_format_correct(tmp_path):
    file = tmp_path / "valid.csv"
    file.write_text("col1,col2\n1,2\n3,4")
    assert validate_csv_format(str(file), expected_cols=2)


def test_validate_csv_format_incorrect_columns(tmp_path):
    file = tmp_path / "invalid.csv"
    file.write_text("col1,col2\n1,2,3")
    with pytest.raises(ValueError):
        validate_csv_format(str(file), expected_cols=2)
