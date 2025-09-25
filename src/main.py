from src.interface.cli import runCLI, runMenu

import sys

if __name__ == "__main__":


    if len(sys.argv) > 1:
        runCLI()
    else:
        runMenu()
