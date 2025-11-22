import pandas as pd
import numpy as np
from typing import Optional, List
from pathlib import Path



def export_to_csv(df: pd.DataFrame, filepath: str, sep: str = ",",
                  index: bool = False, columns: Optional[List[str]] = None,
                  overwrite: bool = False) -> None:
    """Export a DataFrame to CSV format."""
    if df.empty:
        raise ValueError("Cannot export an empty DataFrame to CSV.")
    path = Path(filepath)
    if path.exists() and not overwrite:
        raise FileExistsError(f"File {filepath} already exists. Set overwrite=True to replace.")
    if columns:
        missing = [c for c in columns if c not in df.columns]
        if missing:
            raise KeyError(f"Columns not found in DataFrame: {missing}")
        df_to_save = df[columns]
    else:
        df_to_save = df
    df_to_save.to_csv(filepath, sep=sep, index=index)


def export_to_numpy(df: pd.DataFrame, filepath: str, columns: Optional[list[str]] = None,
                    overwrite: bool = False) -> None:
    """Export a DataFrame to NumPy .npy format."""
    if df.empty:
        raise ValueError("Cannot export an empty DataFrame to NumPy.")
    path = Path(filepath)
    if path.exists() and not overwrite:
        raise FileExistsError(f"File {filepath} already exists. Set overwrite=True to replace.")
    if columns:
        missing = [col for col in columns if col not in df.columns]
        if missing:
            raise KeyError(f"Columns not found in DataFrame: {missing}")
        array = df[columns].to_numpy()
    else:
        array = df.to_numpy()
    np.save(filepath, array)
