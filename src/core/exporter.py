import pandas as pd
import numpy as np
from typing import Optional


def export_to_csv(df: pd.DataFrame, filepath: str, sep: str = ",", index: bool = False) -> None:
    """Export a DataFrame to CSV format."""
    raise NotImplementedError()


def export_to_numpy(df: pd.DataFrame, filepath: str, columns: Optional[list[str]] = None) -> None:
    """Export a DataFrame to NumPy .npy format."""
    raise NotImplementedError()
