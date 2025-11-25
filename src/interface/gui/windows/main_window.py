from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QTableView, QFileDialog, QMessageBox, QInputDialog
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

        # widgets
        self.btnLoad = ui.findChild(QPushButton, "btnLoad")
        self.btnPreviewHead = ui.findChild(QPushButton, "btnPreviewHead")
        self.btnPreviewTail = ui.findChild(QPushButton, "btnPreviewTail")
        self.btnValidate = ui.findChild(QPushButton, "btnValidate")
        self.btnExportCSV = ui.findChild(QPushButton, "btnExportCSV")
        self.btnExportNumPy = ui.findChild(QPushButton, "btnExportNumPy")
        self.tableView = ui.findChild(QTableView, "tableView")


        # connect
        self.btnLoad.clicked.connect(self.load_csv)
        self.btnPreviewHead.clicked.connect(lambda: self.preview(False))
        self.btnPreviewTail.clicked.connect(lambda: self.preview(True))
        self.btnValidate.clicked.connect(self.validate)
        self.btnExportCSV.clicked.connect(self.export_csv)
        self.btnExportNumPy.clicked.connect(self.export_numpy)


    def _set_table(self, df):
        self.tableView.setModel(PandasModel(df))


    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV (*.csv)")
        if not path:
            return
        df = self.controller.load(path)
        self._set_table(df)


    def preview(self, tail=False):
        df = self.controller.preview(10, tail)
        self._set_table(df)


    def validate(self):
        try:
            errors = self.controller.validate_basic()
            if errors:
                QMessageBox.warning(self, "Validation", "\n".join(errors))
            else:
                QMessageBox.information(self, "Validation", "No issues found")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV (*.csv)")
        if path:
            self.controller.export_csv(path)
            QMessageBox.information(self, "Export", "CSV exported")


    def export_numpy(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export NumPy", "", "NumPy (*.npy)")
        if path:
            self.controller.export_numpy(path)
            QMessageBox.information(self, "Export", "NumPy exported")


    # Below are example GUI-driven wrappers for other CLI functions.
    def drop_columns_dialog(self):
        cols, ok = QInputDialog.getText(self, "Drop columns", "Columns (comma-separated):")
        if ok and cols:
            try:
                cols_list = [c.strip() for c in cols.split(",")]
                self.controller.drop_columns(cols_list)
                self._set_table(self.controller.df)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


    def add_column_dialog(self):
        name, ok = QInputDialog.getText(self, "Add column", "New column name:")
        if not ok or not name:
            return
        values, ok = QInputDialog.getText(self, "Add column values", "Comma-separated values:")
        if ok:
            vals = [v.strip() for v in values.split(",")]
        try:
            self.controller.add_column(name, vals)
            self._set_table(self.controller.df)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))