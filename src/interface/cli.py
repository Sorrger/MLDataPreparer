import argparse
import pandas as pd

from src.core.loader import load_csv
from src.core.processor import drop_columns, filter_rows
from src.core.validator import validate_schema
from src.core.exporter import export_to_csv, export_to_numpy


def runCLI():
    parser = argparse.ArgumentParser(
        description="MLDataPreparer CLI - load, process, validate, and export datasets."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Loader ---
    load_parser = subparsers.add_parser("load", help="Load a CSV file")
    load_parser.add_argument("filepath", type=str, help="Path to CSV file")
    load_parser.add_argument("--sep", type=str, default=",", help="CSV separator")

    # --- Processor (drop columns) ---
    drop_parser = subparsers.add_parser("drop", help="Drop columns from dataset")
    drop_parser.add_argument("filepath", type=str, help="Path to CSV file")
    drop_parser.add_argument("columns", nargs="+", help="Column names to drop")

    # --- Validator ---
    val_parser = subparsers.add_parser("validate", help="Validate dataset schema")
    val_parser.add_argument("filepath", type=str, help="Path to CSV file")
    val_parser.add_argument("columns", nargs="+", help="Expected columns")

    # --- Exporter ---
    export_parser = subparsers.add_parser("export", help="Export dataset")
    export_parser.add_argument("filepath", type=str, help="Path to CSV file")
    export_parser.add_argument("--out", type=str, required=True, help="Output file path")
    export_parser.add_argument("--format", choices=["csv", "npy"], default="csv")

    args = parser.parse_args()

    if args.command == "load":
        df = load_csv(args.filepath, sep=args.sep)
        print(df.head())

    elif args.command == "drop":
        df = load_csv(args.filepath)
        df2 = drop_columns(df, args.columns)
        print(df2.head())

    elif args.command == "validate":
        df = load_csv(args.filepath)
        ok = validate_schema(df, args.columns)
        print("Schema valid" if ok else "Schema invalid")

    elif args.command == "export":
        df = load_csv(args.filepath)
        if args.format == "csv":
            export_to_csv(df, args.out)
        else:
            export_to_numpy(df, args.out)
        print(f"Data exported to {args.out} ({args.format})")



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
