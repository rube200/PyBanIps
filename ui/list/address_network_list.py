from PyQt6.QtWidgets import QListWidget, QAbstractItemView, QWidget, QLayout


class AddressNetworkList(QListWidget):
    def __init__(self, parent: QWidget, layout: QLayout):
        super().__init__(parent)

        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setSortingEnabled(True)

        layout.addWidget(self)
