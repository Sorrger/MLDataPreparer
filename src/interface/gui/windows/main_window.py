from PySide6.QtWidgets import (
    QMainWindow, QPushButton, QTableView, QFileDialog, QMessageBox, QToolBar
)
from PySide6.QtGui import QAction
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QMenu

from src.interface.gui.controllers.data_controller import DataController
from src.interface.gui.models.pandas_model import PandasModel

# dialogs
from src.interface.gui.dialogs.drop_columns_dialog import DropColumnsDialog
from src.interface.gui.dialogs.add_column_dialog import AddColumnDialog
from src.interface.gui.dialogs.expression_dialog import ExpressionDialog
from src.interface.gui.dialogs.group_aggregate_dialog import GroupAggregateDialog
from src.interface.gui.dialogs.rolling_dialog import RollingDialog
from src.interface.gui.dialogs.resample_dialog import ResampleDialog
from src.interface.gui.dialogs.derived_column_dialog import DerivedColumnDialog
from src.interface.gui.dialogs.preview_dialog import PreviewDialog
from src.interface.gui.dialogs.separator_dialog import SeparatorDialog


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
        self.btnValidate = ui.findChild(QPushButton, "btnValidate")
        self.btnExportCSV = ui.findChild(QPushButton, "btnExportCSV")
        self.btnExportNumPy = ui.findChild(QPushButton, "btnExportNumPy")
        self.tableView = ui.findChild(QTableView, "tableView")

        # Connect buttons
        self.btnLoad.clicked.connect(self.load_csv)
        self.btnPreviewHead.clicked.connect(self.show_preview_dialog)
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
        act_undo = QAction("Undo", self)
        act_undo.setShortcut("Ctrl+Z")
        act_undo.triggered.connect(self.undo_action)
        self.toolbar.addAction(act_undo)

        act_redo = QAction("Redo", self)
        act_redo.setShortcut("Ctrl+Y")
        act_redo.triggered.connect(self.redo_action)
        self.toolbar.addAction(act_redo)

        self.toolbar.addSeparator()
        act_drop = QAction("Drop columns", self)
        act_drop.triggered.connect(self.show_drop_columns)
        self.toolbar.addAction(act_drop)

        act_add_col = QAction("Add column", self)
        self.toolbar.addAction(act_add_col)

        add_menu = QMenu(self)

        act_add_values = QAction("From values", self)
        act_add_values.triggered.connect(self.show_add_column)

        act_add_expr = QAction("From expression", self)
        act_add_expr.triggered.connect(self.show_add_column_expression)

        act_add_math = QAction("From math (A + B)", self)
        act_add_math.triggered.connect(self.show_add_column_math)

        add_menu.addAction(act_add_values)
        add_menu.addAction(act_add_expr)
        add_menu.addAction(act_add_math)

        act_add_col.setMenu(add_menu)

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
    def undo_action(self):
        df = self.controller.undo()
        if df is not None:
            self.tableView.setModel(PandasModel(df))


    def redo_action(self):
        df = self.controller.redo()
        if df is not None:
            self.tableView.setModel(PandasModel(df))


    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select CSV", "", "CSV (*.csv)"
        )
        if not path:
            return

        dlg = SeparatorDialog(self)
        if not dlg.exec():
            return

        sep = dlg.get_separator()

        try:
            df = self.controller.load(path, sep=sep)
            self.tableView.setModel(PandasModel(df))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # --- VALIDATION ---
    def show_validation_dialog(self):
        if self.controller.df is None:
            QMessageBox.warning(self, "No data", "Load CSV first")
            return

        report = self.controller.quality_report()

        lines = []
        lines.append(f"Rows: {report['rows']}")
        lines.append(f"Columns: {report['columns']}")
        lines.append("")
        lines.append("Missing values:")

        for col, count in report["missing"].items():
            pct = report["missing_pct"][col]
            if count > 0:
                lines.append(f"  {col}: {count} ({pct}%)")

        lines.append("")
        lines.append(f"Duplicate rows: {report['duplicates']}")

        if report["constant_columns"]:
            lines.append("")
            lines.append("Constant columns:")
            for col in report["constant_columns"]:
                lines.append(f"  {col}")

        QMessageBox.information(
            self,
            "Data quality report",
            "\n".join(lines) if len(lines) > 5 else "No issues found"
    )


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
            name, values = dlg.get_data()
            df = self.controller.add_column(name, values)
            self.tableView.setModel(PandasModel(df))


    def show_add_column_expression(self):
        dlg = ExpressionDialog(self, self.controller.df)
        if dlg.exec():
            name, expr = dlg.get_data()
            df = self.controller.add_column_expression(name, expr)
            self.tableView.setModel(PandasModel(df))


    def show_add_column_math(self):
        dlg = DerivedColumnDialog(self, self.controller.df)
        if dlg.exec():
            col1, col2, op, new_name = dlg.get_data()
            df = self.controller.math_column(col1, col2, op, new_name)
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
        dlg = ResampleDialog(self, self.controller.df)
        if dlg.exec():
            col, rule, op = dlg.get_params()
            df = self.controller.resample(col, rule, op)
            self.tableView.setModel(PandasModel(df))


    def show_preview_dialog(self):
        if self.controller.df is None:
            return

        max_rows = len(self.controller.df)
        dlg = PreviewDialog(self, max_rows)

        if dlg.exec():
            rows, mode = dlg.get_params()
            df = self.controller.preview_rows(
                rows,
                tail=(mode == "tail")
            )
            self.tableView.setModel(PandasModel(df))

    
