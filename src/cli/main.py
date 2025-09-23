import argparse
import pandas as pd

from src.core.loader import load_csv
from src.core.processor import drop_columns, filter_rows
from src.core.validator import validate_schema
from src.core.exporter import export_to_csv, export_to_numpy


def main():
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
        print("Schema valid ✅" if ok else "Schema invalid ❌")

    elif args.command == "export":
        df = load_csv(args.filepath)
        if args.format == "csv":
            export_to_csv(df, args.out)
        else:
            export_to_numpy(df, args.out)
        print(f"Data exported to {args.out} ({args.format})")