from sys import argv

from PyQt6.QtWidgets import QApplication

from applications.settings import Settings
from controllers.db_controller import DBController
from controllers.main_controller import MainController
from controllers.ssh_controller import SSHController
from ui.main_window import MainWindow


class MainApplication(QApplication):
    def __init__(self):
        super().__init__(argv)
        self._main_controller = MainController(Settings())

        self.setApplicationDisplayName('Py Ban Ips')

        self._db_controller = DBController(self._main_controller)
        self._ssh_controller = SSHController(self._main_controller)

        self.window = MainWindow(self._main_controller)

        self._main_controller.prepare_data.emit()
        self._main_controller.load_data_to_ui()

    def show(self) -> None:
        self.window.show()
        self.setActiveWindow(self.window)
