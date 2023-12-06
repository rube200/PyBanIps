from PyQt6.QtWidgets import QPushButton, QWidget, QSizePolicy, QLayout


class PushButton12(QPushButton):
    def __init__(self, text: str, parent: QWidget, layout: QLayout):
        super().__init__(text, parent)

        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

        size_policy = self.sizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Policy.Preferred)
        self.setSizePolicy(size_policy)

        layout.addWidget(self)
