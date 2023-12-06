from PyQt6.QtGui import QValidator
from PyQt6.QtWidgets import QLineEdit, QWidget, QLayout


class LineEdit12(QLineEdit):
    def __init__(self, placeholder: str, parent: QWidget, layout: QLayout, validator: QValidator = None):
        super().__init__(parent)

        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

        self.setPlaceholderText(placeholder)
        if validator:
            self.setValidator(validator)

        layout.addWidget(self)
