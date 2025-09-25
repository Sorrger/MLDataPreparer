import typer
from src.core.loader import load_csv
from src.core.processor import drop_columns
from src.core.validator import validate_schema
from src.core.exporter import export_to_csv, export_to_numpy

app = typer.Typer(help="MLDataPreparer CLI - load, process, validate, and export datasets.")


# --- CLI commands (Typer) ----------------------------------------------------

@app.command()
def load(filepath: str, sep: str = ","):
    """Load a CSV file and show preview."""
    df = load_csv(filepath, sep=sep)
    typer.echo(df.head())


@app.command()
def drop(filepath: str, columns: str):
    """Drop one or more columns from dataset (comma-separated)."""
    df = load_csv(filepath)
    df2 = drop_columns(df, columns.split(","))
    typer.echo(df2.head())


@app.command()
def validate(filepath: str, columns: str):
    """Validate dataset schema against expected columns (comma-separated)."""
    df = load_csv(filepath)
    ok = validate_schema(df, columns.split(","))
    typer.echo("Schema valid ✅" if ok else "Schema invalid ❌")


@app.command()
def export(filepath: str, out: str, format: str = "csv"):
    """Export dataset to CSV or NumPy format."""
    df = load_csv(filepath)
    if format == "csv":
        export_to_csv(df, out)
    else:
        export_to_numpy(df, out)
    typer.echo(f"Data exported to {out} ({format})")


# --- Interactive Menu -------------------------------------------------------

def runMenu():
    df = None
    while True:
        print("\n=== MLDataPreparer Menu ===")
        print("1. Load CSV")
        print("2. Drop columns")
        print("3. Validate schema")
        print("4. Export data")
        print("5. Show preview")
        print("0. Exit")

        choice = input("Choose option: ")

        if choice == "1":
            path = input("Enter file path: ")
            sep = input("Separator (default ,): ") or ","
            df = load_csv(path, sep=sep)
            print("Data loaded")

        elif choice == "2":
            if df is None:
                print("Load data first")
                continue
            cols = input("Columns to drop (space separated): ").split()
            df = drop_columns(df, cols)
            print("Columns dropped")

        elif choice == "3":
            if df is None:
                print("Load data first")
                continue
            cols = input("Enter expected columns (space separated): ").split()
            ok = validate_schema(df, cols)
            print("Schema valid" if ok else "Schema invalid")

        elif choice == "4":
            if df is None:
                print("Load data first")
                continue
            out = input("Output file path: ")
            fmt = input("Format (csv/npy): ").lower()
            if fmt == "csv":
                export_to_csv(df, out)
            else:
                export_to_numpy(df, out)
            print(f"Exported to {out} ({fmt})")

        elif choice == "5":
            if df is not None:
                print(df.head())
            else:
                print("No data loaded")

        elif choice == "0":
            break

        else:
            print("Invalid choice")
