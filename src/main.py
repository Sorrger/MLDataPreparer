import sys

from src.interface.cli import app, runMenu

if __name__ == "__main__":
    if len(sys.argv) > 1:
        app()
    else:
        runMenu()
