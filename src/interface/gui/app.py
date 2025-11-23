import sys
import os
from PySide6.QtWidgets import QApplication
from src.interface.gui.windows.main_window import MainWindow

def run():
    app = QApplication(sys.argv)

    base_dir = os.path.dirname(os.path.dirname(__file__))
    ui_file = os.path.join(base_dir, "ui", "main_window.ui")
    ui_file = os.path.abspath(ui_file)

    win = MainWindow(ui_file)
    win.show()

    sys.exit(app.exec())
