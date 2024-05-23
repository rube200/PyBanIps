from datetime import UTC
from datetime import datetime
from typing import Type
from typing import TypeVar

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from controllers.main_controller import MainController
from models.address_network_base import AddressNetworkBase
from models.analyse_address import AnalyseAddress
from models.banned_network import BannedNetwork
from models.database_mode_base import DatabaseModelBase
from models.last_log_date import LastLogDate
from utils.ip_address_utils import IPvAddress
from utils.ip_address_utils import ip_address
from utils.ip_network_utils import IPvNetwork
from utils.ip_network_utils import ip_network


class DBController:
    def __init__(self, main_controller: MainController):
        self.__main_controller = main_controller
        self.settings = main_controller.get_settings

        self.__main_controller.add_address_db = self.add_address
        self.__main_controller.bulk_add_addresses_db.connect(self.bulk_add_addresses)
        self.__main_controller.get_addresses_db = self.get_addresses
        self.__main_controller.get_networks_db = self.get_networks
        self.__main_controller.get_last_load_date = self.get_last_load_date
        self.__main_controller.prepare_data.connect(self.prepare_data)

        self._cache_analyse_addresses: None | list[AnalyseAddress] = None
        self._cache_banned_networks: None | list[BannedNetwork] = None

        self._db_engine = create_engine(self.settings().db_connection)
        DatabaseModelBase.metadata.create_all(self._db_engine)

    T_ANB = TypeVar('T_ANB', bound=AddressNetworkBase)

    def _add_anb_to_db(self, adb: T_ANB, cache_list: None | list[T_ANB]) -> T_ANB:
        with Session(self._db_engine, expire_on_commit=False) as session:
            session.add(adb)
            session.commit()

        if cache_list is not None:
            cache_list.append(adb)

        return adb

    def _add_address_db(self, address: IPvAddress) -> AnalyseAddress:
        analyse_address = AnalyseAddress(address)
        return self._add_anb_to_db(analyse_address, self._cache_analyse_addresses)

    def _add_network_db(self, network: IPvNetwork) -> BannedNetwork:
        banned_network = BannedNetwork(ip=network)
        return self._add_anb_to_db(banned_network, self._cache_banned_networks)

    def _create_network(self, address: IPvAddress) -> IPvNetwork:
        network = ip_network(address)
        max_parts = 2 if network.version == 4 else 8

        for max_count in range(max_parts):
            super_network = network.supernet(8)

            if not self._is_network_exceeded(super_network):
                break

            network = super_network

        return network

    def _is_network_exceeded(self, super_network: IPvNetwork) -> bool:
        count = 1
        max_addresses = self.settings().max_addresses
        if max_addresses < 5:
            return False

        for banned_network in self._cache_banned_networks:
            if (banned_network.ip.version != super_network.version
                    or super_network.prefixlen >= banned_network.ip.prefixlen):
                continue

            if super_network.supernet_of(banned_network.ip):
                count += 1

            if count >= max_addresses:
                return True

        return False

    @staticmethod
    def _get_sub_networks(network: BannedNetwork, cache_list: list[T_ANB], skip_equal: bool) -> list[T_ANB]:
        subnetwork_list = []

        for adb in cache_list:
            if skip_equal and adb == network:
                continue

            if adb in network:
                subnetwork_list.append(adb)

        return subnetwork_list

    def _increment_address_count(self, analyse_address: AnalyseAddress) -> None:
        with Session(self._db_engine) as session:
            session.query(AnalyseAddress).filter_by(ip=analyse_address.ip).update(
                {AnalyseAddress.count: AnalyseAddress.count + 1})
            session.commit()
        analyse_address.count += 1

    def _index_of_address(self, address: IPvAddress) -> int:
        cache = self._cache_analyse_addresses
        return cache.index(address) if address in cache else -1

    def _is_address_banned(self, address: IPvAddress) -> bool:
        cache = self._cache_banned_networks

        for network in cache:
            if address in network:
                return True

        return False

    def _remove_address_db(self, address: AnalyseAddress):
        with Session(self._db_engine) as session:
            session.delete(address)
            session.commit()

        self._cache_analyse_addresses.remove(address)

    def _remove_sub_network(self, ban_network: BannedNetwork) -> None:
        addresses_to_remove = self._get_sub_networks(ban_network, self._cache_analyse_addresses, False)
        networks_to_remove = self._get_sub_networks(ban_network, self._cache_banned_networks, True)

        self._cache_analyse_addresses = self.remove_adb_in_bulk(AnalyseAddress, addresses_to_remove,
                                                                self._cache_analyse_addresses)
        self._cache_banned_networks = self.remove_adb_in_bulk(BannedNetwork, networks_to_remove,
                                                              self._cache_banned_networks)

        match len(addresses_to_remove):
            case 0:
                self.__main_controller.set_networks_ui.emit()

            case 1:
                self.__main_controller.remove_address_ui.emit(addresses_to_remove.pop())
                self.__main_controller.set_networks_ui.emit()

            case _:
                self.__main_controller.load_data_to_ui()

    def add_address(self, address_raw: str) -> None | str:
        if not address_raw:
            return f'Address \'{address_raw}\' is not valid.'

        address = ip_address(address_raw)
        if not address:
            return f'Address \'{address_raw}\' is not valid.'

        if self._is_address_banned(address):
            return f'Address \'{address_raw}\' is already banned!'

        settings = self.settings()
        address_index = self._index_of_address(address)

        match address_index:
            case -1:
                if settings.max_detects > 1:
                    analyse_address = self._add_address_db(address)
                    self.__main_controller.add_address_ui.emit(analyse_address)
                    return None
                else:
                    analyse_address = None

            case _:
                analyse_address = self._cache_analyse_addresses[address_index]
                if analyse_address.count < settings.max_detects - 1:
                    self._increment_address_count(analyse_address)
                    self.__main_controller.update_address_ui.emit(analyse_address)
                    return None

        network = self._create_network(address)
        banned_network = self._add_network_db(network)
        if network.prefixlen == network.max_prefixlen:
            if analyse_address:
                self._remove_address_db(analyse_address)

            self.__main_controller.add_network_ui.emit(banned_network)
            self.__main_controller.remove_address_ui.emit(analyse_address)
            return None

        self._remove_sub_network(banned_network)
        return None

    def bulk_add_addresses(self, addresses: list[IPvAddress], last_log_date: datetime):  # todo try refactor
        add_to_analyse: list[AnalyseAddress] = []
        add_to_banned: list[BannedNetwork] = []

        remove_from_analyse: list[AnalyseAddress] = []
        remove_from_banned: list[BannedNetwork] = []

        settings = self.settings()

        for address in addresses:
            if self._is_address_banned(address):
                continue

            address_index = self._index_of_address(address)
            if address_index == -1:
                analyse_address = AnalyseAddress(address)
                self._cache_analyse_addresses.append(analyse_address)

                add_to_analyse.append(analyse_address)
                continue

            analyse_address = self._cache_analyse_addresses[address_index]
            if analyse_address.count < settings.max_detects - 1:
                analyse_address.count += 1
                continue

            network = self._create_network(address)
            banned_network = BannedNetwork(ip=network)

            self._cache_banned_networks.append(banned_network)
            add_to_banned.append(banned_network)
            if network.prefixlen == network.max_prefixlen:
                self._cache_analyse_addresses.remove(analyse_address)
                if analyse_address in add_to_analyse:
                    add_to_analyse.remove(analyse_address)
                continue

            addresses_to_remove = self._get_sub_networks(banned_network, self._cache_analyse_addresses, False)
            for address_to_remove in addresses_to_remove:
                self._cache_analyse_addresses.remove(address_to_remove)
                if address_to_remove in add_to_analyse:
                    add_to_analyse.remove(address_to_remove)
                else:
                    remove_from_analyse.remove(address_to_remove)

            networks_to_remove = self._get_sub_networks(banned_network, self._cache_banned_networks, True)
            for network_to_remove in networks_to_remove:
                self._cache_banned_networks.remove(network_to_remove)
                if network_to_remove in add_to_banned:
                    add_to_banned.remove(network_to_remove)
                else:
                    remove_from_banned.remove(network_to_remove)

        remove_analyse_ips = [address.ip for address in remove_from_analyse]
        remove_banned_ips = [network.ip for network in remove_from_banned]

        with Session(self._db_engine, expire_on_commit=False) as session:
            if add_to_analyse:
                session.add_all(add_to_analyse)

            if add_to_banned:
                session.add_all(add_to_banned)

            if remove_analyse_ips:
                session.query(AnalyseAddress).where(AnalyseAddress.ip.in_(remove_analyse_ips)).delete()

            if remove_banned_ips:
                session.query(BannedNetwork).where(BannedNetwork.ip.in_(remove_banned_ips)).delete()

            session.merge(LastLogDate(last_load_date=last_log_date))

            session.commit()

        self.__main_controller.load_data_to_ui()

    def get_addresses(self) -> list[AnalyseAddress]:
        return self._cache_analyse_addresses

    def get_networks(self) -> list[BannedNetwork]:
        return self._cache_banned_networks

    def get_last_load_date(self) -> None | datetime:
        with Session(self._db_engine) as session:
            date = session.query(LastLogDate.last_load_date).one_or_none()
            session.commit()
            return date[0].astimezone(UTC) if date else date

    def prepare_data(self) -> None:
        self.refresh_cache()
        self.verify_and_repair_data()

    def remove_adb_in_bulk(self, tp: Type[T_ANB], adb_list: list[T_ANB], cache_list: None | list[T_ANB]
                           ) -> None | list[T_ANB]:
        if not adb_list:
            return cache_list

        ips = [adb.ip for adb in adb_list]
        with Session(self._db_engine) as session:
            # noinspection PyUnresolvedReferences
            session.query(tp).where(tp.ip.in_(ips)).delete()
            session.commit()

        if cache_list is None:
            return cache_list

        return [i for i in cache_list if i not in adb_list]

    def refresh_cache(self) -> None:
        with Session(self._db_engine, expire_on_commit=False) as session:
            self._cache_analyse_addresses = session.query(AnalyseAddress).all()
            self._cache_banned_networks = session.query(BannedNetwork).all()
            session.commit()

    def verify_and_repair_data(self) -> None:  # todo adding check if address count is to high and needs to be banned
        addresses_to_remove: [AnalyseAddress] = []
        networks_to_remove: [BannedNetwork] = []

        for network in self._cache_banned_networks:
            data_to_remove = self._get_sub_networks(network, self._cache_analyse_addresses, False)
            addresses_to_remove.extend(data_to_remove)

            data_to_remove = self._get_sub_networks(network, self._cache_banned_networks, True)
            networks_to_remove.extend(data_to_remove)

        self._cache_analyse_addresses = self.remove_adb_in_bulk(AnalyseAddress, addresses_to_remove,
                                                                self._cache_analyse_addresses)
        self._cache_banned_networks = self.remove_adb_in_bulk(BannedNetwork, networks_to_remove,
                                                              self._cache_banned_networks)
