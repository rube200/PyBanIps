from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QLabel, QWidget, QLayout


class Label12(QLabel):
    def __init__(self, text: str, parent: QWidget, layout: QLayout = None, color: QColor = None):
        super().__init__(text, parent)

        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

        if color:
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.WindowText, color)
            self.setPalette(palette)

        if layout is not None:
            layout.addWidget(self)
