import pytest
import pandas as pd
import numpy as np
import os

from src.core.exporter import export_to_csv, export_to_numpy


# --- Fixtures ----------------------------------------------------------------

@pytest.fixture
def simple_df():
    """Reusable DataFrame for export tests."""
    return pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})


# --- export_to_csv tests -----------------------------------------------------

def test_export_to_csv_creates_file(tmp_path, simple_df):
    """export_to_csv should create a CSV file with expected content."""
    file = tmp_path / "data.csv"
    export_to_csv(simple_df, file)

    assert file.exists()
    df2 = pd.read_csv(file)
    assert list(df2.columns) == ["a", "b"]
    assert df2.shape == (3, 2)


def test_export_to_csv_with_separator(tmp_path, simple_df):
    """export_to_csv should allow custom separators."""
    file = tmp_path / "data.csv"
    export_to_csv(simple_df, file, sep=";")

    content = file.read_text()
    assert ";" in content


def test_export_to_csv_empty_dataframe(tmp_path):
    """export_to_csv should raise ValueError if DataFrame is empty."""
    file = tmp_path / "data.csv"
    df = pd.DataFrame()
    with pytest.raises(ValueError):
        export_to_csv(df, file)


# --- export_to_numpy tests ---------------------------------------------------

def test_export_to_numpy_creates_file(tmp_path, simple_df):
    """export_to_numpy should create a .npy file with expected shape."""
    file = tmp_path / "data.npy"
    export_to_numpy(simple_df, file)

    assert file.exists()
    arr = np.load(file, allow_pickle=False)
    assert arr.shape == (3, 2)


def test_export_to_numpy_with_columns(tmp_path, simple_df):
    """export_to_numpy should export only selected columns."""
    file = tmp_path / "subset.npy"
    export_to_numpy(simple_df, file, columns=["a"])

    arr = np.load(file, allow_pickle=False)
    assert arr.shape == (3, 1)
    assert arr[:, 0].tolist() == [1, 2, 3]


def test_export_to_numpy_with_missing_column(tmp_path, simple_df):
    """export_to_numpy should raise KeyError if column does not exist."""
    file = tmp_path / "fail.npy"
    with pytest.raises(KeyError):
        export_to_numpy(simple_df, file, columns=["nonexistent"])


def test_export_to_numpy_empty_dataframe(tmp_path):
    """export_to_numpy should raise ValueError if DataFrame is empty."""
    file = tmp_path / "fail.npy"
    df = pd.DataFrame()
    with pytest.raises(ValueError):
        export_to_numpy(df, file)

def test_export_to_csv_with_columns(tmp_path, simple_df):
    """CSV export only some columns"""
    file = tmp_path / "cols.csv"
    export_to_csv(simple_df, file, columns=["a"])
    assert file.exists()
    df2 = pd.read_csv(file)
    assert list(df2.columns) == ["a"]

def test_export_to_csv_overwrite_behavior(tmp_path, simple_df):
    file = tmp_path / "data.csv"
    export_to_csv(simple_df, file)
    # writing again without overwrite should raise
    with pytest.raises(FileExistsError):
        export_to_csv(simple_df, file)
    # with overwrite True should succeed
    export_to_csv(simple_df, file, overwrite=True)
    assert file.exists()

def test_export_to_csv_select_columns(tmp_path, simple_df):
    """CSV export only some columns"""
    file = tmp_path / "subset.csv"
    export_to_csv(simple_df, file, columns=["a"])
    df2 = pd.read_csv(file)
    assert list(df2.columns) == ["a"]

def test_export_to_csv_overwrite(tmp_path, simple_df):
    """CSV overwrite=True"""
    file = tmp_path / "test.csv"
    export_to_csv(simple_df, file)
    export_to_csv(simple_df, file, overwrite=True)
    assert file.exists()

def test_export_to_numpy_overwrite(tmp_path, simple_df):
    """NumPy export overwrite fails unless allowed"""
    file = tmp_path / "test.npy"
    export_to_numpy(simple_df, file)
    with pytest.raises(FileExistsError):
        export_to_numpy(simple_df, file)

def test_export_to_numpy_overwrite_true(tmp_path, simple_df):
    """NumPy export overwrite=True"""
    file = tmp_path / "test.npy"
    export_to_numpy(simple_df, file)
    export_to_numpy(simple_df, file, overwrite=True)
    arr = np.load(file)
    assert arr.shape == (3, 2)
