from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QTableView, QFileDialog, QMessageBox
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from src.interface.gui.controllers.data_controller import DataController
from src.interface.gui.models.pandas_model import PandasModel


class MainWindow(QMainWindow):
    def __init__(self, ui_path):
        super().__init__()

        loader = QUiLoader()
        file = QFile(ui_path)
        file.open(QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        self.setCentralWidget(ui)

        self.controller = DataController()

        # --- UI widgets
        self.btnLoad = ui.findChild(QPushButton, "btnLoad")
        self.btnPreviewHead = ui.findChild(QPushButton, "btnPreviewHead")
        self.btnPreviewTail = ui.findChild(QPushButton, "btnPreviewTail")
        self.btnValidate = ui.findChild(QPushButton, "btnValidate")
        self.btnExportCSV = ui.findChild(QPushButton, "btnExportCSV")
        self.btnExportNumPy = ui.findChild(QPushButton, "btnExportNumPy")
        self.tableView = ui.findChild(QTableView, "tableView")

        # --- Connect signals
        self.btnLoad.clicked.connect(self.load_csv)
        self.btnPreviewHead.clicked.connect(lambda: self.preview(False))
        self.btnPreviewTail.clicked.connect(lambda: self.preview(True))
        self.btnValidate.clicked.connect(self.validate)
        self.btnExportCSV.clicked.connect(self.export_csv)
        self.btnExportNumPy.clicked.connect(self.export_numpy)

    # -------------------------------------------------------------------------
    # LOAD CSV
    # -------------------------------------------------------------------------
    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV (*.csv)")
        if not path:
            return
        
        df = self.controller.load(path)
        self.tableView.setModel(PandasModel(df))

    # -------------------------------------------------------------------------
    # PREVIEW
    # -------------------------------------------------------------------------
    def preview(self, tail=False):
        df = self.controller.preview(10, tail)
        self.tableView.setModel(PandasModel(df))

    # -------------------------------------------------------------------------
    # VALIDATE
    # -------------------------------------------------------------------------
    def validate(self):
        errors = self.controller.validate_basic()
        if errors:
            QMessageBox.warning(self, "Validation Errors", "\n".join(errors))
        else:
            QMessageBox.information(self, "OK", "No validation issues found")

    # -------------------------------------------------------------------------
    # EXPORT
    # -------------------------------------------------------------------------
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV (*.csv)")
        if path:
            self.controller.export_csv(path)
            QMessageBox.information(self, "Success", "CSV Exported")

    def export_numpy(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export NumPy", "", "NumPy (*.npy)")
        if path:
            self.controller.export_numpy(path)
            QMessageBox.information(self, "Success", "NumPy Exported")
