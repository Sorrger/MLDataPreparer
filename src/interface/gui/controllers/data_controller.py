import pandas as pd

from src.core.loader import load_csv, preview_dataframe
from src.core.exporter import export_to_csv, export_to_numpy
from src.core.validator import validate_no_missing
from src.core.processor import drop_columns

class DataController:
    def __init__(self):
        self.df: pd.DataFrame | None = None

    def load(self, path: str):
        self.df = load_csv(path)
        return self.df


    def preview(self, n: int, tail=False):
        return preview_dataframe(self.df, n, tail)

    def validate_basic(self):
        """Return string messages instead of raising exceptions."""
        errors = []

        try:
            validate_no_missing(self.df)
        except Exception as e:
            errors.append(str(e))

        return errors

    def drop_columns(self, cols):
        self.df = drop_columns(self.df, cols)
        return self.df

    def export_csv(self, path):
        export_to_csv(self.df, path, overwrite=True)

    def export_numpy(self, path):
        export_to_numpy(self.df, path, overwrite=True)
