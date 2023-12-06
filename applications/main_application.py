from sys import argv

from PyQt6.QtWidgets import QApplication

from applications.settings import Settings
from controllers.db_controller import DBController
from controllers.main_controller import MainController
from controllers.ssh_controller import SSHController
from ui.main_window import MainWindow


class MainApplication(MainController, QApplication):
    def __init__(self):
        super().__init__(Settings(), argv)
        self.setApplicationDisplayName('Py Ban Ips')

        self._db_controller = DBController(self)
        self._ssh_controller = SSHController(self)

        self.window = MainWindow(self)

        self.prepare_data()
        self.load_data_to_ui()

    def show(self) -> None:
        self.window.show()
        self.setActiveWindow(self.window)
