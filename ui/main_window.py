from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow

from controllers.main_controller import MainController
from ui.main_widget import MainWidget


class MainWindow(QMainWindow):
    def __init__(self, main_controller: MainController):
        super().__init__()

        size = QSize(960, 540)
        self.setMinimumSize(size)
        # self.setPalette(DarkTheme())

        self.main_widget = MainWidget(self, main_controller)
        self.setCentralWidget(self.main_widget)
