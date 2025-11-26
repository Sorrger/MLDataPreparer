from PySide6.QtWidgets import (
QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
)


class ResampleDialog(QDialog):
    def __init__(self, parent=None, df=None):
        super().__init__(parent)
        self.setWindowTitle("Resample time series")
        self.resize(520, 220)


        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Datetime column name:"))
        self.dtcol = QLineEdit(self)
        self.layout.addWidget(self.dtcol)


        self.layout.addWidget(QLabel("Frequency (e.g. D,W,M):"))
        self.freq = QLineEdit(self)
        self.layout.addWidget(self.freq)


        self.layout.addWidget(QLabel("Aggregations (col:sum,col2:mean):"))
        self.agg = QLineEdit(self)
        self.layout.addWidget(self.agg)


        self.btn_ok = QPushButton("Resample", self)
        self.btn_ok.clicked.connect(self.accept)
        self.layout.addWidget(self.btn_ok)


    def get_params(self):
        agg_raw = [p.strip() for p in self.agg.text().split(",")] if self.agg.text().strip() else []
        agg = {k: v for k, v in (pair.split(":") for pair in agg_raw)} if agg_raw else {}
        return self.dtcol.text().strip(), self.freq.text().strip(), agg