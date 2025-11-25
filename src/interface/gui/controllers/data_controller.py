import pandas as pd
from typing import Optional, List, Dict, Any, Set


from src.core.loader import (
    load_csv, 
    preview_dataframe, 
    get_dataframe_stat_summary, 
    set_column_names
)
from src.core.exporter import export_to_csv, export_to_numpy
from src.core.processor import (
    drop_columns, add_column, create_column_from_existing,
    drop_rows_by_index, drop_rows_by_condition, drop_empty_columns,
    math_operation, group_and_aggregate, filter_text, resample_time_series,
    rolling_stat, filter_rows
)
from src.core.validator import (
    validate_schema, validate_no_missing, validate_value_ranges,
    validate_unique, validate_allowed_values, check_missing_values
)

class DataController:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.path: Optional[str] = None


    # ------------------ Loading / Preview ------------------
    def load(self, filepath: str, sep: str = ",") -> pd.DataFrame:
        df = load_csv(filepath, sep=sep)
        self.df = df
        self.path = filepath
        return df
    def preview(self, n: int = 5, tail: bool = False) -> pd.DataFrame:
        return preview_dataframe(self.df, n, tail)


    def stats(self) -> Dict[str, Any]:
        return get_dataframe_stat_summary(self.df)

    # ------------------ Processing (wrap core functions) ------------------
    def drop_columns(self, cols: List[str]) -> pd.DataFrame:
        self.df = drop_columns(self.df, cols)
        return self.df


    def add_column(self, name: str, values: List[Any]) -> pd.DataFrame:
        self.df = add_column(self.df, name, values)
        return self.df


    def create_column_from_existing(self, new_name: str, base: str, func):
        # func is a callable that receives df and returns a Series
        self.df = create_column_from_existing(self.df, new_name, func)
        return self.df


    def drop_rows_by_index(self, indexes: List[int]):
        self.df = drop_rows_by_index(self.df, indexes)
        return self.df


    def drop_rows_by_condition(self, column: str, value: str):
        self.df = drop_rows_by_condition(self.df, lambda row: str(row[column]) == value)
        return self.df


    def filter_where(self, column: str, value: str):
        self.df = filter_rows(self.df, lambda row: str(row[column]) == value)
        return self.df


    def group_and_aggregate(self, by: List[str], agg: Dict[str, List[str]]):
        self.df = group_and_aggregate(self.df, by, agg)
        return self.df


    def text_filter(self, column: str, mode: str, pattern: str):
        self.df = filter_text(self.df, column, mode, pattern)
        return self.df


    def rolling(self, column: str, window: int, func: str = "mean"):
        series = rolling_stat(self.df, column, window, func)
        name = f"rolling_{func}_{column}_{window}"
        self.df[name] = series
        return self.df


    def resample(self, datetime_col: str, freq: str, agg_funcs: Dict[str, str]):
        self.df = resample_time_series(self.df, datetime_col, freq, agg_funcs)
        return self.df

    # ------------------ Validation ------------------
    def validate_schema(self, cols: List[str]):
        return validate_schema(self.df, cols)


    def validate_no_missing(self, columns: Optional[List[str]] = None):
        return validate_no_missing(self.df, columns)


    def validate_value_ranges(self, column: str, minv: float = None, maxv: float = None):
        return validate_value_ranges(self.df, column, minv, maxv)


    def validate_unique(self, columns: List[str]):
        return validate_unique(self.df, columns)


    def validate_allowed_values(self, column: str, allowed: Set[Any]):
        return validate_allowed_values(self.df, column, allowed)


    def missing_summary(self):
        return check_missing_values(self.df)

    # ------------------ Export ------------------
    def export_csv(self, path: str, overwrite: bool = True):
        export_to_csv(self.df, path, overwrite=overwrite)


    def export_numpy(self, path: str, overwrite: bool = True):
        export_to_numpy(self.df, path, overwrite=overwrite)


    # ------------------ Helpers ------------------
    def ensure_id(self, id_col: str = "id", start: int = 1, set_as_index: bool = True):
        """
        Ensure the dataframe has an 'id' column. If missing it will be created.
        Optionally set as index.
        """
        if id_col not in self.df.columns:
            self.df[id_col] = range(start, start + len(self.df))
        if set_as_index:
            self.df = self.df.set_index(id_col)
        return self.df