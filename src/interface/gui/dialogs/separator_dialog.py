from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton


class SeparatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSV separator")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Choose CSV separator:"))

        self.combo = QComboBox()
        self.combo.addItem("Comma (,)", ",")
        self.combo.addItem("Semicolon (;)", ";")
        self.combo.addItem("Tab (\\t)", "\t")
        self.combo.addItem("Pipe (|)", "|")

        layout.addWidget(self.combo)

        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def get_separator(self) -> str:
        return self.combo.currentData()
