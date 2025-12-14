from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton
)

class DerivedColumnDialog(QDialog):
    def __init__(self, parent=None, df=None):
        super().__init__(parent)
        self.setWindowTitle("Create column from others")
        self.resize(400, 220)

        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel("First column:"))
        self.col1 = QComboBox(self)
        self.col1.addItems(df.columns)
        self.layout.addWidget(self.col1)

        self.layout.addWidget(QLabel("Second column:"))
        self.col2 = QComboBox(self)
        self.col2.addItems(df.columns)
        self.layout.addWidget(self.col2)

        self.layout.addWidget(QLabel("Operation:"))
        self.op = QComboBox(self)
        self.op.addItems(["sum", "diff", "prod", "mean"])
        self.layout.addWidget(self.op)

        self.layout.addWidget(QLabel("New column name:"))
        self.name = QLineEdit(self)
        self.layout.addWidget(self.name)

        self.btn = QPushButton("Create", self)
        self.btn.clicked.connect(self.accept)
        self.layout.addWidget(self.btn)

    def get_data(self):
        return (
            self.col1.currentText(),
            self.col2.currentText(),
            self.op.currentText(),
            self.name.text().strip()
        )
