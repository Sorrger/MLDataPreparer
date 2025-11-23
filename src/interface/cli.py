import os
import typer
import pandas as pd
from rich import print
from rich.table import Table

# --- Core imports ------------------------------------------------------------
from src.core.loader import (
    load_csv,
    preview_dataframe,
    get_dataframe_stat_summary,
    set_column_names,
)
from src.core.processor import (
    drop_columns,
    add_column,
    create_column_from_existing,
    drop_rows_by_index,
    drop_rows_by_condition,
    drop_empty_columns,
    math_operation,
    group_and_aggregate,
    filter_text,
    resample_time_series,
    rolling_stat,
)
from src.core.validator import (
    validate_schema,
    validate_no_missing,
    validate_value_ranges,
    validate_unique,
    validate_allowed_values,
)
from src.core.exporter import export_to_csv, export_to_numpy


# -----------------------------------------------------------------------------
# Typer Application
# -----------------------------------------------------------------------------
app = typer.Typer(
    help="MLDataPreparer CLI – load, clean, transform, validate and export datasets.",
    rich_markup_mode="rich"
)

STATE = {"df": None, "path": None}


# -----------------------------------------------------------------------------
# Utility: Pretty DataFrame Printer
# -----------------------------------------------------------------------------
def _show_df(df: pd.DataFrame, title="Preview"):
    table = Table(title=title)
    for col in df.columns:
        table.add_column(str(col))
    for _, row in df.iterrows():
        table.add_row(*[str(x) for x in row.tolist()])
    print(table)


# -----------------------------------------------------------------------------
# Submodules
# -----------------------------------------------------------------------------
load_app = typer.Typer(help="Load & preview datasets")
process_app = typer.Typer(help="Modify / transform datasets")
validate_app = typer.Typer(help="Validate datasets")
export_app = typer.Typer(help="Save datasets")

app.add_typer(load_app, name="load")
app.add_typer(process_app, name="process")
app.add_typer(validate_app, name="validate")
app.add_typer(export_app, name="export")


# -----------------------------------------------------------------------------
# LOAD COMMANDS
# -----------------------------------------------------------------------------
@load_app.command("csv")
def load_csv_cmd(filepath: str, sep: str = ","):
    try:
        df = load_csv(filepath, sep=sep)
        STATE["df"] = df
        STATE["path"] = filepath
        print(f"[green]Loaded dataset from:[/green] {filepath}")
        _show_df(df.head(), "Preview")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@load_app.command("preview")
def preview_cmd(n: int = 5, tail: bool = False):
    df = STATE["df"]
    if df is None:
        print("[red]Load data first[/red]")
        raise typer.Exit()
    _show_df(preview_dataframe(df, n, tail))


@load_app.command("stats")
def stats_cmd():
    df = STATE["df"]
    if df is None:
        print("[red]Load data first[/red]")
        raise typer.Exit()

    stats = get_dataframe_stat_summary(df)
    print("[cyan]Dataset Summary[/cyan]")
    for k, v in stats.items():
        print(f"[yellow]{k}[/yellow]: {v}")


# -----------------------------------------------------------------------------
# PROCESSING COMMANDS
# -----------------------------------------------------------------------------
@process_app.command("drop-columns")
def drop_columns_cmd(cols: str):
    df = STATE["df"]
    if df is None:
        print("[red]Load data first[/red]")
        raise typer.Exit()
    try:
        STATE["df"] = drop_columns(df, cols.split(","))
        print("[green]Columns dropped[/green]")
        _show_df(STATE["df"])
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@process_app.command("add-column")
def add_column_cmd(name: str, values: str):
    """
    Add a column: values must be comma-separated (e.g. 1,2,3)
    """
    df = STATE["df"]
    if df is None:
        raise typer.Exit()
    try:
        vals = [x.strip() for x in values.split(",")]
        STATE["df"] = add_column(df, name, vals)
        print("[green]Column added[/green]")
        _show_df(STATE["df"])
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@process_app.command("create-column")
def create_column_cmd(new_name: str, base: str):
    """
    Create a new column based on one other column.  
    Formula: new = base * 2  
    """
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    if base not in df.columns:
        print("[red]Base column not found[/red]")
        raise typer.Exit()

    try:
        STATE["df"] = create_column_from_existing(
            df, new_name, lambda df: df[base] * 2
        )
        print("[green]Column created[/green]")
        _show_df(STATE["df"])
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@process_app.command("drop-rows")
def drop_rows_cmd(indexes: str):
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    try:
        idx = [int(i) for i in indexes.split(",")]
        STATE["df"] = drop_rows_by_index(df, idx)
        print("[green]Rows dropped[/green]")
        _show_df(STATE["df"])
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@process_app.command("drop-where")
def drop_where_cmd(column: str, value: str):
    """
    Example: drop all rows where column == value
    """
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    try:
        STATE["df"] = drop_rows_by_condition(df, lambda row: str(row[column]) == value)
        print("[green]Rows dropped[/green]")
        _show_df(STATE["df"])
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@process_app.command("filter-where")
def filter_where_cmd(column: str, value: str):
    """
    Keep only rows where column == value
    """
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    try:
        STATE["df"] = df[df[column].astype(str) == value]
        print("[green]Rows filtered[/green]")
        _show_df(STATE["df"])
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@process_app.command("group")
def group_cmd(by: str, metrics: str):
    """
    metrics format: col:sum,col2:mean
    """
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    agg_dict = {k: [v] for k, v in (pair.split(":") for pair in metrics.split(","))}

    try:
        grouped = group_and_aggregate(df, by.split(","), agg_dict)
        STATE["df"] = grouped
        print("[green]Grouped successfully[/green]")
        _show_df(grouped)
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@process_app.command("text-filter")
def text_filter_cmd(column: str, mode: str, pattern: str):
    df = STATE["df"]
    if df is None:
        raise typer.Exit()
    try:
        STATE["df"] = filter_text(df, column, mode, pattern)
        print("[green]Filter applied[/green]")
        _show_df(STATE["df"])
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


@process_app.command("rolling")
def rolling_cmd(column: str, window: int, func: str = "mean"):
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    try:
        result = rolling_stat(df, column, window, func)
        df["rolling_" + func] = result
        STATE["df"] = df
        print("[green]Rolling column computed[/green]")
        _show_df(df)
    except Exception as e:
        print(f"[red]Error:[/red] {e}")


# -----------------------------------------------------------------------------
# VALIDATION COMMANDS
# -----------------------------------------------------------------------------
@validate_app.command("schema")
def validate_schema_cmd(cols: str):
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    ok = validate_schema(df, cols.split(","))
    print("[green]Schema valid[/green]" if ok else "[red]Schema invalid[/red]")


@validate_app.command("unique")
def validate_unique_cmd(cols: str):
    df = STATE["df"]
    if df is None:
        raise typer.Exit()
    validate_unique(df, cols.split(","))
    print("[green]Unique constraint OK[/green]")


@validate_app.command("no-missing")
def validate_no_missing_cmd(cols: str = ""):
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    cols_list = cols.split(",") if cols else None
    validate_no_missing(df, cols_list)
    print("[green]No missing values[/green]")


@validate_app.command("range")
def validate_range_cmd(column: str, min_value: float = None, max_value: float = None):
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    validate_value_ranges(df, column, min_value, max_value)
    print("[green]Value range OK[/green]")


@validate_app.command("allowed")
def validate_allowed_cmd(column: str, allowed: str):
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    allowed_vals = set(allowed.split(","))
    validate_allowed_values(df, column, allowed_vals)
    print("[green]Allowed values OK[/green]")


# -----------------------------------------------------------------------------
# EXPORT COMMANDS
# -----------------------------------------------------------------------------
@export_app.command("csv")
def export_csv_cmd(out: str, overwrite: bool = False):
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    export_to_csv(df, out, overwrite=overwrite)
    print(f"[green]Saved CSV to[/green] {out}")


@export_app.command("npy")
def export_npy_cmd(out: str, overwrite: bool = False):
    df = STATE["df"]
    if df is None:
        raise typer.Exit()

    export_to_numpy(df, out, overwrite=overwrite)
    print(f"[green]Saved NPY to[/green] {out}")


# -----------------------------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------------------------
def runCLI():
    app()

import os

# ============================================================
# SAFE INPUT HELPERS
# ============================================================

def ask_int(prompt, allow_empty=False):
    """Ask for integer with validation."""
    while True:
        val = input(prompt).strip()
        if val == "" and allow_empty:
            return None
        try:
            return int(val)
        except ValueError:
            print("[red]Please enter a valid integer[/red]")


def ask_list(prompt, sep=",", allow_empty=False):
    """Ask for comma-separated list safely."""
    while True:
        val = input(prompt).strip()
        if val == "" and allow_empty:
            return None
        if val == "":
            print("[red]Input cannot be empty[/red]")
            continue
        return [v.strip() for v in val.split(sep)]


def ensure_loaded():
    if STATE["df"] is None:
        print("[red]Load data first[/red]")
        return False
    return True


# ============================================================
# LOAD MENU
# ============================================================

def menu_load():
    while True:
        print("\n--- LOAD DATA ---")
        print("1. Load CSV file")
        print("0. Back")

        choice = input("Choose option: ").strip()

        if choice == "0":
            return

        elif choice == "1":
            while True:
                path = input("Enter CSV path (ENTER to cancel): ").strip()
                if path == "":
                    print("[yellow]Canceled[/yellow]")
                    break

                if not os.path.exists(path):
                    print("[red]File does not exist. Try again.[/red]")
                    continue

                sep = input("Separator (ENTER for ,): ").strip() or ","

                try:
                    df = load_csv(path, sep)
                    STATE["df"] = df
                    STATE["path"] = path
                    print("[green]Loaded successfully[/green]")
                    _show_df(df.head())
                    break
                except Exception as e:
                    print(f"[red]Error:[/red] {e}")
                    if input("Retry? (y/n): ").strip().lower() != "y":
                        break


# ============================================================
# PREVIEW MENU
# ============================================================

def menu_preview():
    if not ensure_loaded():
        return

    while True:
        n = input("Rows to preview (ENTER for 5, or 'b' to go back): ").strip()
        if n.lower() == "b":
            return

        n = int(n) if n else 5
        try:
            _show_df(preview_dataframe(STATE["df"], n))
            return
        except Exception as e:
            print(f"[red]Error:[/red] {e}")


# ============================================================
# STATS MENU
# ============================================================

def menu_stats():
    if not ensure_loaded():
        return
    try:
        stats = get_dataframe_stat_summary(STATE["df"])
        print("[cyan]Dataset Summary[/cyan]")
        for k, v in stats.items():
            print(f"[yellow]{k}:[/yellow] {v}")
    except Exception as e:
        print("[red]Error:[/red]", e)


# ============================================================
# PROCESSING MENU
# ============================================================

def menu_processing():
    if not ensure_loaded():
        return

    while True:
        print("\n--- PROCESSING ---")
        print("1. Drop columns")
        print("2. Drop rows by index")
        print("3. Drop rows by condition")
        print("4. Add column")
        print("5. Text filter")
        print("6. Group & aggregate")
        print("0. Back")

        sub = input("Choose option: ").strip()
        if sub == "0":
            return

        try:
            # -------------------
            if sub == "1":
                cols = ask_list("Columns to drop (comma): ")
                STATE["df"] = drop_columns(STATE["df"], cols)
                print("[green]Dropped[/green]")
                _show_df(STATE["df"])

            # -------------------
            elif sub == "2":
                idx = ask_list("Row indexes (comma): ")
                idx = [int(i) for i in idx]
                STATE["df"] = drop_rows_by_index(STATE["df"], idx)
                print("[green]Rows removed[/green]")
                _show_df(STATE["df"])

            # -------------------
            elif sub == "3":
                col = input("Column: ").strip()
                val = input("Value to match: ").strip()
                STATE["df"] = drop_rows_by_condition(STATE["df"], lambda row: str(row[col]) == val)
                print("[green]Rows removed[/green]")
                _show_df(STATE["df"])

            # -------------------
            elif sub == "4":
                name = input("New column name: ").strip()
                vals = ask_list("Values (comma): ")
                STATE["df"] = add_column(STATE["df"], name, vals)
                print("[green]Column added[/green]")
                _show_df(STATE["df"])

            # -------------------
            elif sub == "5":
                col = input("Column: ").strip()
                mode = input("Mode (contains / startswith / endswith): ").strip()
                pat = input("Pattern: ").strip()
                STATE["df"] = filter_text(STATE["df"], col, mode, pat)
                print("[green]Filtered[/green]")
                _show_df(STATE["df"])

            # -------------------
            elif sub == "6":
                group_cols = ask_list("Group by (comma): ")
                raw = ask_list("Aggregations (format col:sum,col2:mean): ")
                agg = {k: [v] for k, v in (p.split(":") for p in raw)}
                STATE["df"] = group_and_aggregate(STATE["df"], group_cols, agg)
                print("[green]Grouped[/green]")
                _show_df(STATE["df"])

        except Exception as e:
            print(f"[red]Error:[/red] {e}")


# ============================================================
# VALIDATION MENU
# ============================================================

def menu_validation():
    if not ensure_loaded():
        return

    while True:
        print("\n--- VALIDATION ---")
        print("1. Schema check")
        print("2. Unique check")
        print("3. Missing values")
        print("4. Value range")
        print("5. Allowed values")
        print("0. Back")

        sub = input("Choose option: ").strip()

        if sub == "0":
            return

        try:
            if sub == "1":
                cols = ask_list("Expected columns (comma): ")
                print(validate_schema(STATE["df"], cols))

            elif sub == "2":
                cols = ask_list("Columns (comma): ")
                validate_unique(STATE["df"], cols)
                print("[green]Unique OK[/green]")

            elif sub == "3":
                cols = ask_list("Columns (comma, ENTER for all): ", allow_empty=True)
                validate_no_missing(STATE["df"], cols)
                print("[green]No missing[/green]")

            elif sub == "4":
                col = input("Column: ").strip()
                minv = input("Min (ENTER skip): ").strip()
                maxv = input("Max (ENTER skip): ").strip()

                validate_value_ranges(
                    STATE["df"], col,
                    float(minv) if minv else None,
                    float(maxv) if maxv else None
                )
                print("[green]Range OK[/green]")

            elif sub == "5":
                col = input("Column: ").strip()
                allowed = set(ask_list("Allowed values (comma): "))
                validate_allowed_values(STATE["df"], col, allowed)
                print("[green]Allowed values OK[/green]")

        except Exception as e:
            print(f"[red]Error:[/red] {e}")


# ============================================================
# EXPORT MENU
# ============================================================

def menu_export():
    if not ensure_loaded():
        return

    while True:
        print("\n--- EXPORT ---")
        print("1. Save CSV")
        print("2. Save NumPy (.npy)")
        print("0. Back")

        sub = input("Choose option: ").strip()

        if sub == "0":
            return

        try:
            if sub == "1":
                out = input("Output filename: ").strip()
                export_to_csv(STATE["df"], out)
                print("[green]Saved CSV[/green]")

            elif sub == "2":
                out = input("Output filename: ").strip()
                export_to_numpy(STATE["df"], out)
                print("[green]Saved NPY[/green]")

        except Exception as e:
            print(f"[red]Error:[/red] {e}")


# ============================================================
# MAIN MENU
# ============================================================

def runMenu():
    while True:
        print("\n=== MLDataPreparer Interactive Menu ===")
        print("1. Load CSV")
        print("2. Preview")
        print("3. Stats summary")
        print("4. Processing")
        print("5. Validation")
        print("6. Export")
        print("0. Exit")

        choice = input("Choose option: ").strip()

        if choice == "0":
            print("Bye!")
            return

        elif choice == "1":
            menu_load()

        elif choice == "2":
            menu_preview()

        elif choice == "3":
            menu_stats()

        elif choice == "4":
            menu_processing()

        elif choice == "5":
            menu_validation()

        elif choice == "6":
            menu_export()

        else:
            print("[red]Invalid option[/red]")
