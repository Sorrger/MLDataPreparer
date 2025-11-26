from PySide6.QtWidgets import (
QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox
)


class ValidationDialog(QDialog):
    def __init__(self, parent=None, df=None):
        super().__init__(parent)
        self.setWindowTitle("Validation helper")
        self.resize(480, 180)


        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Choose validation:"))
        self.kind = QComboBox(self)
        self.kind.addItems(["no_missing", "schema", "unique", "range", "allowed"])
        self.layout.addWidget(self.kind)


        self.layout.addWidget(QLabel("Parameters (comma separated or appropriate format):"))
        self.params = QLineEdit(self)
        self.layout.addWidget(self.params)


        self.btn_ok = QPushButton("Run", self)
        self.btn_ok.clicked.connect(self.accept)
        self.layout.addWidget(self.btn_ok)


    def get_params(self):
        return self.kind.currentText(), self.params.text().strip()