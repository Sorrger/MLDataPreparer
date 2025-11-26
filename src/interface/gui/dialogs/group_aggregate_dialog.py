from PySide6.QtWidgets import (
QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
)


class GroupAggregateDialog(QDialog):
    def __init__(self, parent=None, df=None):
        super().__init__(parent)
        self.setWindowTitle("Group & Aggregate")
        self.resize(480, 180)


        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Group by columns (comma-separated):"))
        self.group = QLineEdit(self)
        self.layout.addWidget(self.group)


        self.layout.addWidget(QLabel("Aggregations (format: col:sum,col2:mean):"))
        self.agg = QLineEdit(self)
        self.layout.addWidget(self.agg)


        self.btn_ok = QPushButton("Apply", self)
        self.btn_ok.clicked.connect(self.accept)
        self.layout.addWidget(self.btn_ok)


    def get_params(self):
        by = [c.strip() for c in self.group.text().split(",")] if self.group.text().strip() else []
        raw = [p.strip() for p in self.agg.text().split(",")] if self.agg.text().strip() else []
        agg = {k: v for k, v in (pair.split(":") for pair in raw)} if raw else {}
        return by, agg