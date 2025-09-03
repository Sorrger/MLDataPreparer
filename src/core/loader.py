from typing import Optional, Dict, List
import pandas as pd

def load_csv(
        filepath: str,
        sep: str = ",",
        header: Optional[int] = 0,
        encoding: str = "utf-8",
        na_values: Optional[List[str]] = None
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
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing CSV file: {e}")


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
    

def set_column_names(df: pd.DataFrame, names: List[str]) -> pd.DataFrame:
    """Manually set column names in a DataFrame."""
    if df.shape[1] != len(names):
        raise ValueError("Number of names doesn't match")
    df.columns = names 
    return df


def validate_csv_format(filepath: str, expected_cols: Optional[int] = None) -> bool:
    """Check basic integrity of a CSV file before loading."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            if not first_line:
                raise ValueError("CSV file is empty")

            cols = first_line.split(",")
            if expected_cols is not None and len(cols) != expected_cols:
                raise ValueError("Wrong number of columns")

            for line in f:
                values = line.strip().split(",")
                if expected_cols is not None and len(values) != expected_cols:
                    raise ValueError(
                        f"Inconsistent column number in row: {line.strip()}"
                    )

        return True
    except FileNotFoundError:
        raise FileNotFoundError("File not found")