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


# -------------------------------------------------------------------------
# INTERACTIVE MENU (full functionality)
# -------------------------------------------------------------------------
def runMenu():
    while True:
        print("\n[bold cyan]=== MLDataPreparer Interactive Menu ===[/bold cyan]")
        print("1. Load CSV")
        print("2. Preview")
        print("3. Stats summary")
        print("4. PROCESSING")
        print("5. VALIDATION")
        print("6. EXPORT")
        print("0. Exit")

        choice = input("Choose option: ").strip()

        # ---------------------------
        # MAIN ACTIONS
        # ---------------------------

        if choice == "1":
            path = input("Enter CSV path: ")
            sep = input("Separator (default ,): ") or ","
            load_csv_cmd(path, sep)

        elif choice == "2":
            n = int(input("Rows to preview: "))
            preview_cmd(n)

        elif choice == "3":
            stats_cmd()

        # ---------------------------
        # PROCESSING SUBMENU
        # ---------------------------
        elif choice == "4":
            while True:
                print("\n[bold magenta]--- PROCESSING ---[/bold magenta]")
                print("1. Drop columns")
                print("2. Add column")
                print("3. Create column (base * 2)")
                print("4. Drop rows by index")
                print("5. Drop rows by condition")
                print("6. Filter rows by value")
                print("7. Group & aggregate")
                print("8. Text filter")
                print("9. Rolling window")
                print("0. Back")
                p = input("Choose processing option: ").strip()

                if p == "1":
                    cols = input("Columns to drop (comma-separated): ")
                    drop_columns_cmd(cols)

                elif p == "2":
                    name = input("New column name: ")
                    vals = input("Values (comma-separated): ")
                    add_column_cmd(name, vals)

                elif p == "3":
                    new = input("New column name: ")
                    base = input("Base column: ")
                    create_column_cmd(new, base)

                elif p == "4":
                    idx = input("Row indexes to drop (comma-separated): ")
                    drop_rows_cmd(idx)

                elif p == "5":
                    col = input("Column name: ")
                    val = input("Drop rows where column == value: ")
                    drop_where_cmd(col, val)

                elif p == "6":
                    col = input("Column name: ")
                    val = input("Keep only rows where column == value: ")
                    filter_where_cmd(col, val)

                elif p == "7":
                    by = input("Group by (comma-separated): ")
                    metrics = input("Aggregations (format col:sum,col2:mean): ")
                    group_cmd(by, metrics)

                elif p == "8":
                    col = input("Column: ")
                    mode = input("Mode (contains/startswith/endswith): ")
                    patt = input("Pattern: ")
                    text_filter_cmd(col, mode, patt)

                elif p == "9":
                    col = input("Column: ")
                    window = int(input("Window size: "))
                    func = input("Function (mean/sum/max/min): ") or "mean"
                    rolling_cmd(col, window, func)

                elif p == "0":
                    break

        # ---------------------------
        # VALIDATION SUBMENU
        # ---------------------------
        elif choice == "5":
            while True:
                print("\n[bold yellow]--- VALIDATION ---[/bold yellow]")
                print("1. Validate schema")
                print("2. Validate unique")
                print("3. Validate no missing")
                print("4. Validate range")
                print("5. Validate allowed values")
                print("0. Back")
                v = input("Choose validation option: ").strip()

                if v == "1":
                    cols = input("Expected columns (comma-separated): ")
                    validate_schema_cmd(cols)

                elif v == "2":
                    cols = input("Columns to check (comma-separated): ")
                    validate_unique_cmd(cols)

                elif v == "3":
                    cols = input("Columns (empty for all): ")
                    validate_no_missing_cmd(cols)

                elif v == "4":
                    col = input("Column: ")
                    minv = input("Min (or blank): ")
                    maxv = input("Max (or blank): ")
                    minv = float(minv) if minv else None
                    maxv = float(maxv) if maxv else None
                    validate_range_cmd(col, minv, maxv)

                elif v == "5":
                    col = input("Column: ")
                    allowed = input("Allowed values (comma-separated): ")
                    validate_allowed_cmd(col, allowed)

                elif v == "0":
                    break

        # ---------------------------
        # EXPORT SUBMENU
        # ---------------------------
        elif choice == "6":
            while True:
                print("\n[bold green]--- EXPORT ---[/bold green]")
                print("1. Export CSV")
                print("2. Export NPY")
                print("0. Back")
                e = input("Choose export option: ")

                if e == "1":
                    out = input("Output CSV: ")
                    export_csv_cmd(out)

                elif e == "2":
                    out = input("Output NPY: ")
                    export_npy_cmd(out)

                elif e == "0":
                    break

        # ---------------------------
        # EXIT
        # ---------------------------
        elif choice == "0":
            print("[cyan]Exiting interactive menu[/cyan]")
            break

        else:
            print("[red]Invalid choice[/red]")
