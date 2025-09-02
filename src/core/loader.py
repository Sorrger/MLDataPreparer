from os import name
from typing import Optional, Dict
import pandas as pd

def load_csv(
        filepath: str,
        sep: str = ",",
        header: Optional[int] = 0,
        encoding: str = "utf-8",
        na_values: Optional[list[str]] = None
) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""

    try:
        df = pd.read_csv(
            filepath,
            sep = sep,
            header = header,
            encoding = encoding,
            na_values = na_values
        )
        if df.empty:
            raise ValueError("CSV file is empty")
        return df
    
    except FileNotFoundError:
        raise FileNotFoundError("File not found")
    #Need to add more excepts


def preview_dataframe(
        df: pd.DataFrame,
        row_number,
        tail: bool = False
) -> pd.DataFrame:
    """Return a preview of the DataFrame."""
    if(row_number <= 0):
        raise ValueError("row_number cannot be <= 0")
    if tail:
        return df.tail(row_number)
    else:
        return df.head(row_number)



def get_dataframe_stat_summary(
        df: pd.DataFrame
) -> Dict[str, object]:
    """Return summary statistics and structure of a DataFrame."""
    return {
        "row_count": df.shape[0],
        "column_count": df.shape[1],
        "missing_values": df.isna().sum().to_dict()
    }
    

def set_column_names(df: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    """Manually set column names in a DataFrame."""
    if df.shape[1] != len(names):
        raise ValueError("Number of names doesn't match")
    df.columns = names 
    return df

def validate_csv_format(filepath: str, expected_cols: Optional[int] = None) -> bool:
    """Check basic integrity of a CSV file before loading.

    Args:
        filepath (str): _description_
        expected_cols (int | None, optional): _description_. Defaults to None.

    Raises:
        NotImplementedError: _description_

    Returns:
        bool: _description_
    """
    raise NotImplementedError()