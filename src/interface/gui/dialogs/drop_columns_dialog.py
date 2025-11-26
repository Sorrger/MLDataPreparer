from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton


class DropColumnsDialog(QDialog):
    def __init__(self, parent=None, df=None):
        super().__init__(parent)
        self.setWindowTitle("Drop columns")
        self.resize(400, 120)


        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Columns to drop (comma-separated):"))
        self.input = QLineEdit(self)
        self.layout.addWidget(self.input)


        self.btn_ok = QPushButton("Drop", self)
        self.btn_ok.clicked.connect(self.accept)
        self.layout.addWidget(self.btn_ok)


    def get_columns(self):
        text = self.input.text().strip()
        if not text:
            return []
        return [c.strip() for c in text.split(",")]