from datetime import datetime
from ipaddress import IPv4Address
from typing import Callable

from applications.settings import DEFAULT_APP_MAX_DETECTS_TO_BAN
from applications.settings import Settings
from models.analyse_address import AnalyseAddress
from models.banned_network import BannedNetwork


class MainController:
    def __init__(self, settings: Settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__settings = settings
        if self.__settings.max_detects < 1:
            self.__settings.max_detects = DEFAULT_APP_MAX_DETECTS_TO_BAN
            # todo finish

        if self.__settings.max_addresses < 5:
            # todo finish
            pass

        self.__add_address_db: Callable[[str], None | str] | None = None
        self.__add_address_ui: Callable[[AnalyseAddress], None] | None = None
        self.__add_network_ui: Callable[[BannedNetwork], None] | None = None
        self.__bulk_add_addresses_db: Callable[[list[IPv4Address], datetime], None] | None = None
        self.__get_addresses_db: Callable[[], list[AnalyseAddress]] | None = None
        self.__get_networks_db: Callable[[], list[BannedNetwork]] | None = None
        self.__get_last_load_date: Callable[[], None | datetime] | None = None
        self.__load_logs_ssh: Callable[[], None] | None = None
        self.__prepare_data: Callable[[], None] | None = None
        self.__remove_address_ui: Callable[[AnalyseAddress], None] | None = None
        self.__set_address_ui: Callable[[], None] | None = None
        self.__set_networks_ui: Callable[[], None] | None = None
        self.__update_address_ui: Callable[[AnalyseAddress], None] | None = None
        self.__write_bans_ssh: Callable[[], None] | None = None

    def get_settings(self) -> Settings:
        return self.__settings

    def set_add_address_db_callback(self, callback: Callable[[str], None | str]) -> None:
        self.__add_address_db = callback

    def set_add_address_ui_callback(self, callback: Callable[[AnalyseAddress], None]) -> None:
        self.__add_address_ui = callback

    def set_add_network_ui_callback(self, callback: Callable[[BannedNetwork], None]) -> None:
        self.__add_network_ui = callback

    def set_bulk_add_addresses_db_callback(self, callback: Callable[[list[IPv4Address], datetime], None]) -> None:
        self.__bulk_add_addresses_db = callback

    def set_get_addresses_db_callback(self, callback: Callable[[], list[AnalyseAddress]]) -> None:
        self.__get_addresses_db = callback

    def set_get_networks_db_callback(self, callback: Callable[[], list[BannedNetwork]]) -> None:
        self.__get_networks_db = callback

    def set_get_last_load_date_callback(self, callback: Callable[[], None | datetime]) -> None:
        self.__get_last_load_date = callback

    def set_load_logs_ssh_callback(self, callback: Callable[[], None]) -> None:
        self.__load_logs_ssh = callback

    def set_prepare_data_callback(self, callback: Callable[[], None]) -> None:
        self.__prepare_data = callback

    def set_remove_address_ui_callback(self, callback: Callable[[AnalyseAddress], None]) -> None:
        self.__remove_address_ui = callback

    def set_set_addresses_ui_callback(self, callback: Callable[[], None]) -> None:
        self.__set_address_ui = callback

    def set_set_networks_ui_callback(self, callback: Callable[[], None]) -> None:
        self.__set_networks_ui = callback

    def set_update_address_ui_callback(self, callback: Callable[[AnalyseAddress], None]) -> None:
        self.__update_address_ui = callback

    def set_write_bans_callback(self, callback: Callable[[], None]) -> None:
        self.__write_bans_ssh = callback

    def add_address_db(self, text: str) -> str:
        return self.__add_address_db(text)

    def add_address_ui(self, address: AnalyseAddress) -> None:
        self.__add_address_ui(address)

    def add_network_ui(self, network: BannedNetwork) -> None:
        self.__add_network_ui(network)

    def bulk_add_addresses_db(self, addresses: list[IPv4Address], last_log_date: datetime) -> None:
        self.__bulk_add_addresses_db(addresses, last_log_date)

    def get_addresses_db(self) -> list[AnalyseAddress]:
        return self.__get_addresses_db()

    def get_last_load_date(self) -> None | datetime:
        return self.__get_last_load_date()

    def get_networks_db(self) -> list[BannedNetwork]:
        return self.__get_networks_db()

    def load_data_to_ui(self) -> None:
        self.set_addresses_ui()
        self.set_networks_ui()

    def load_logs_ssh(self) -> None:
        self.__load_logs_ssh()

    def prepare_data(self) -> None:
        self.__prepare_data()

    def remove_address_ui(self, address: AnalyseAddress) -> None:
        self.__remove_address_ui(address)

    def set_addresses_ui(self) -> None:
        return self.__set_address_ui()

    def set_networks_ui(self) -> None:
        return self.__set_networks_ui()

    def update_address_ui(self, address: AnalyseAddress) -> None:
        self.__update_address_ui(address)

    def write_bans_ssh(self) -> None:
        self.__write_bans_ssh()
