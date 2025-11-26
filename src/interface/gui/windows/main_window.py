from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QTableView, QFileDialog, QMessageBox, QToolBar
)
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from src.interface.gui.controllers.data_controller import DataController
from src.interface.gui.models.pandas_model import PandasModel

# dialogs
from src.interface.gui.dialogs.drop_columns_dialog import DropColumnsDialog
from src.interface.gui.dialogs.add_column_dialog import AddColumnDialog
from src.interface.gui.dialogs.group_aggregate_dialog import GroupAggregateDialog
from src.interface.gui.dialogs.rolling_dialog import RollingDialog
from src.interface.gui.dialogs.resample_dialog import ResampleDialog
from src.interface.gui.dialogs.validation_dialog import ValidationDialog


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

        # UI widgets
        self.btnLoad = ui.findChild(QPushButton, "btnLoad")
        self.btnPreviewHead = ui.findChild(QPushButton, "btnPreviewHead")
        self.btnPreviewTail = ui.findChild(QPushButton, "btnPreviewTail")
        self.btnValidate = ui.findChild(QPushButton, "btnValidate")
        self.btnExportCSV = ui.findChild(QPushButton, "btnExportCSV")
        self.btnExportNumPy = ui.findChild(QPushButton, "btnExportNumPy")
        self.tableView = ui.findChild(QTableView, "tableView")

        # Connect buttons
        self.btnLoad.clicked.connect(self.load_csv)
        self.btnPreviewHead.clicked.connect(lambda: self.preview(False))
        self.btnPreviewTail.clicked.connect(lambda: self.preview(True))
        self.btnValidate.clicked.connect(self.show_validation_dialog)
        self.btnExportCSV.clicked.connect(self.export_csv)
        self.btnExportNumPy.clicked.connect(self.export_numpy)

        # Toolbar
        self.toolbar = QToolBar("Actions", self)
        self.addToolBar(self.toolbar)

        self.add_processing_actions()

    # -----------------------------------------------------
    # Toolbar Actions
    # -----------------------------------------------------
    def add_processing_actions(self):
        act_drop = QAction("Drop columns", self)
        act_drop.triggered.connect(self.show_drop_columns)
        self.toolbar.addAction(act_drop)

        act_add = QAction("Add column", self)
        act_add.triggered.connect(self.show_add_column)
        self.toolbar.addAction(act_add)

        act_group = QAction("Group & aggregate", self)
        act_group.triggered.connect(self.show_group_aggregate)
        self.toolbar.addAction(act_group)

        act_roll = QAction("Rolling", self)
        act_roll.triggered.connect(self.show_rolling)
        self.toolbar.addAction(act_roll)

        act_resample = QAction("Resample", self)
        act_resample.triggered.connect(self.show_resample)
        self.toolbar.addAction(act_resample)

    # -----------------------------------------------------
    # GUI Actions
    # -----------------------------------------------------
    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV (*.csv)")
        if not path:
            return

        df = self.controller.load(path)
        self.tableView.setModel(PandasModel(df))

    def preview(self, tail=False):
        df = self.controller.preview(10, tail)
        self.tableView.setModel(PandasModel(df))

    # --- VALIDATION ---
    def show_validation_dialog(self):
        dlg = ValidationDialog(self)
        if dlg.exec():
            kind, params = dlg.get_params()
            msgs = self.controller.validate(kind, params)
            if msgs:
                QMessageBox.warning(self, "Validation errors", "\n".join(msgs))
            else:
                QMessageBox.information(self, "OK", "No issues found")

    # -----------------------------------------------------
    # EXPORT
    # -----------------------------------------------------
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV (*.csv)")
        if path:
            self.controller.export_csv(path)
            QMessageBox.information(self, "Success", "CSV exported")

    def export_numpy(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export NumPy", "", "NumPy (*.npy)")
        if path:
            self.controller.export_numpy(path)
            QMessageBox.information(self, "Success", "NumPy exported")

    # -----------------------------------------------------
    # Data processing dialogs
    # -----------------------------------------------------
    def show_drop_columns(self):
        dlg = DropColumnsDialog(self, self.controller.df)
        if dlg.exec():
            cols = dlg.get_columns()
            df = self.controller.drop_columns(cols)
            self.tableView.setModel(PandasModel(df))

    def show_add_column(self):
        dlg = AddColumnDialog(self)
        if dlg.exec():
            name, expr = dlg.get_data()
            df = self.controller.add_column(name, expr)
            self.tableView.setModel(PandasModel(df))

    def show_group_aggregate(self):
        dlg = GroupAggregateDialog(self, self.controller.df)
        if dlg.exec():
            gcol, op = dlg.get_params()
            df = self.controller.group_and_aggregate(gcol, op)
            self.tableView.setModel(PandasModel(df))

    def show_rolling(self):
        dlg = RollingDialog(self)
        if dlg.exec():
            col, window, op = dlg.get_params()
            df = self.controller.rolling(col, window, op)
            self.tableView.setModel(PandasModel(df))

    def show_resample(self):
        dlg = ResampleDialog(self)
        if dlg.exec():
            col, rule, op = dlg.get_data()
            df = self.controller.resample(col, rule, op)
            self.tableView.setModel(PandasModel(df))
