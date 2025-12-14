from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSpinBox,
    QComboBox, QPushButton
)

class PreviewDialog(QDialog):
    def __init__(self, parent=None, max_rows=0):
        super().__init__(parent)
        self.setWindowTitle("Preview rows")
        self.resize(300, 220)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Number of rows:"))
        self.rows = QSpinBox()
        self.rows.setRange(1, max_rows)
        self.rows.setValue(min(20, max_rows))
        layout.addWidget(self.rows)

        layout.addWidget(QLabel("Mode:"))
        self.mode = QComboBox()
        self.mode.addItems(["Head", "Tail"])
        layout.addWidget(self.mode)

        btn = QPushButton("Preview")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def get_params(self):
        return (
            self.rows.value(),
            self.mode.currentText().lower()
        )
