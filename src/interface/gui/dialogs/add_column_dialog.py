from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class AddColumnDialog(QDialog):
    def __init__(self, parent=None, df=None):
        super().__init__(parent)
        self.setWindowTitle("Add column")
        self.resize(400, 160)


        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("New column name:"))
        self.name = QLineEdit(self)
        self.layout.addWidget(self.name)


        self.layout.addWidget(QLabel("Values (comma-separated):"))
        self.values = QLineEdit(self)
        self.layout.addWidget(self.values)


        self.btn_ok = QPushButton("Add", self)
        self.btn_ok.clicked.connect(self.accept)
        self.layout.addWidget(self.btn_ok)


    def get_data(self):
        nm = self.name.text().strip()
        vals = [v.strip() for v in self.values.text().split(",")] if self.values.text().strip() else []
        return nm, vals