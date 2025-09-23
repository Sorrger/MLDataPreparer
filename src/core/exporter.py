import pandas as pd
import numpy as np
from typing import Optional


def export_to_csv(df: pd.DataFrame, filepath: str, sep: str = ",", index: bool = False) -> None:
    """Export a DataFrame to CSV format."""
    if df.empty:
        raise ValueError("Cannot export an empty DataFrame to CSV.")
    df.to_csv(filepath, sep=sep, index=index)


def export_to_numpy(df: pd.DataFrame, filepath: str, columns: Optional[list[str]] = None) -> None:
    """Export a DataFrame to NumPy .npy format."""
    if df.empty:
        raise ValueError("Cannot export an empty DataFrame to NumPy.")
    if columns:
        missing = [col for col in columns if col not in df.columns]
        if missing:
            raise KeyError(f"Columns not found in DataFrame: {missing}")
        array = df[columns].to_numpy()
    else:
        array = df.to_numpy()
    np.save(filepath, array)
