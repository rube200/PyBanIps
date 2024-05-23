from datetime import datetime
from typing import Callable

from PyQt6.QtCore import pyqtSignal, QObject

from applications.settings import DEFAULT_APP_MAX_DETECTS_TO_BAN
from applications.settings import Settings
from models.analyse_address import AnalyseAddress
from models.banned_network import BannedNetwork


class MainController(QObject):
    add_address_ui = pyqtSignal(AnalyseAddress)
    add_network_ui = pyqtSignal(BannedNetwork)
    bulk_add_addresses_db = pyqtSignal(list, datetime)
    load_logs_ssh = pyqtSignal()
    prepare_data = pyqtSignal()
    remove_address_ui = pyqtSignal(AnalyseAddress)
    set_address_ui = pyqtSignal()
    set_networks_ui = pyqtSignal()
    update_address_ui = pyqtSignal(AnalyseAddress)
    write_bans_ssh = pyqtSignal()

    add_address_db: Callable[[str], None | str] | None = None
    get_addresses_db: Callable[[], list[AnalyseAddress]] | None = None
    get_last_load_date: Callable[[], None | datetime] | None = None
    get_networks_db: Callable[[], list[BannedNetwork]] | None = None

    def __init__(self, settings: Settings):
        super().__init__()

        self.__settings = settings
        if self.__settings.max_detects < 1:
            self.__settings.max_detects = DEFAULT_APP_MAX_DETECTS_TO_BAN
            # todo finish

        if self.__settings.max_addresses < 5:
            # todo finish
            pass

    def get_settings(self) -> Settings:
        return self.__settings

    # noinspection PyUnresolvedReferences
    def load_data_to_ui(self) -> None:
        self.set_address_ui.emit()
        self.set_networks_ui.emit()
