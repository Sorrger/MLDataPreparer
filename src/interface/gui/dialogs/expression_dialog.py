from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit
)

class ExpressionDialog(QDialog):
    def __init__(self, parent=None, df=None):
        super().__init__(parent)
        self.setWindowTitle("Add column (expression)")
        self.resize(480, 260)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("New column name:"))
        self.name = QLineEdit(self)
        layout.addWidget(self.name)

        layout.addWidget(QLabel("Expression (use column names):"))
        self.expr = QTextEdit(self)
        self.expr.setPlaceholderText("(A + B + C) / 3")
        layout.addWidget(self.expr)

        layout.addWidget(QLabel(f"Available columns: {', '.join(df.columns)}"))

        btn = QPushButton("Create")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def get_data(self):
        return (
            self.name.text().strip(),
            self.expr.toPlainText().strip()
        )
