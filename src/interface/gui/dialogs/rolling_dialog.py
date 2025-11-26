from PySide6.QtWidgets import (
QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton
)


class RollingDialog(QDialog):
    def __init__(self, parent=None, df=None):
        super().__init__(parent)
        self.setWindowTitle("Rolling statistic")
        self.resize(420, 160)


        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Column:"))
        self.col = QLineEdit(self)
        self.layout.addWidget(self.col)


        self.layout.addWidget(QLabel("Window (rows):"))
        self.win = QSpinBox(self)
        self.win.setMinimum(1)
        self.win.setValue(3)
        self.layout.addWidget(self.win)


        self.layout.addWidget(QLabel("Function:"))
        self.func = QComboBox(self)
        self.func.addItems(["mean", "sum", "min", "max", "std"])
        self.layout.addWidget(self.func)


        self.btn_ok = QPushButton("Compute", self)
        self.btn_ok.clicked.connect(self.accept)
        self.layout.addWidget(self.btn_ok)


    def get_params(self):
        return self.col.text().strip(), int(self.win.value()), self.func.currentText()