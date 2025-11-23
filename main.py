import sys

from src.interface.cli import runCLI, runMenu
from src.interface.gui.app import run

if __name__ == "__main__":
    if len(sys.argv) > 1:
        runCLI()
    else:
        #runMenu()
        run()
