from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem

from models.address_network_base import AddressNetworkBase
from models.analyse_address import AnalyseAddress
from models.banned_network import BannedNetwork
from utils.ip_address_utils import IPvAddress, ip_address
from utils.ip_network_utils import IPvNetwork, ip_network


def get_address_from_str(value: str) -> IPvAddress | IPvNetwork:
    str_address = value.split('-')[0].strip()
    address = ip_address(str_address)
    if address:
        return address

    return ip_network(str_address)


class AddressNetworkItem(QListWidgetItem):
    def __init__(self, parent: QListWidget, address: AddressNetworkBase):
        super().__init__(str(address), parent=parent, type=QListWidgetItem.ItemType.UserType)

        self.ip = address.ip
        flags = Qt.ItemFlag
        self.setFlags(flags.ItemIsSelectable | flags.ItemIsEnabled)

        font = self.font()
        font.setPointSize(12)
        self.setFont(font)

    @staticmethod
    def _get_address(other: QListWidgetItem) -> IPvAddress | IPvNetwork:
        value = other.text()
        return get_address_from_str(value)

    def __check_operator(self, other: object, operator: str) -> None | bool:
        if operator == '!=':  # just in case
            return not self == other

        match other:
            case AnalyseAddress() | BannedNetwork():
                # noinspection PyUnresolvedReferences
                ip = other.ip
            case AddressNetworkItem():
                if operator == '==':
                    return super().__eq__(other)
                # noinspection PyUnresolvedReferences
                ip = other.ip
            case IPv4Address() | IPv6Address() | IPv4Network() | IPv6Network():
                ip = other
            case QListWidgetItem():
                # noinspection PyTypeChecker
                ip = self._get_address(other)
            case str():
                # noinspection PyTypeChecker
                ip = get_address_from_str(other)
            case _:
                ip = None

        if ip is None:
            return None

        match operator:
            case '<':
                # noinspection PyUnresolvedReferences
                if self.ip.version == ip.version:
                    # noinspection PyTypeChecker
                    return self.ip < ip
                # noinspection PyUnresolvedReferences
                return self.ip.version < ip.version

            case '<=':
                # noinspection PyUnresolvedReferences
                if self.ip.version == ip.version:
                    # noinspection PyTypeChecker
                    return self.ip <= ip
                # noinspection PyUnresolvedReferences
                return self.ip.version <= ip.version

            case '>':
                # noinspection PyUnresolvedReferences
                if self.ip.version == ip.version:
                    # noinspection PyTypeChecker
                    return self.ip > ip
                # noinspection PyUnresolvedReferences
                return self.ip.version > ip.version

            case '>=':
                # noinspection PyUnresolvedReferences
                if self.ip.version == ip.version:
                    return self.ip >= ip
                # noinspection PyUnresolvedReferences
                return self.ip.version >= ip.version

            case '==':
                # noinspection PyUnresolvedReferences
                return self.ip.version == ip.version and self.ip == ip

            case _:
                return None

    def __eq__(self, other: object) -> bool:
        result = self.__check_operator(other, '==')
        if result is not None:
            return result

        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __ge__(self, other: QListWidgetItem) -> bool:
        result = self.__check_operator(other, '>=')
        if result is not None:
            return result

        return super().__ge__(other)

    def __gt__(self, other: QListWidgetItem) -> bool:
        result = self.__check_operator(other, '>')
        if result is not None:
            return result

        return super().__gt__(other)

    def __le__(self, other: QListWidgetItem) -> bool:
        result = self.__check_operator(other, '<=')
        if result is not None:
            return result

        return super().__le__(other)

    def __lt__(self, other: QListWidgetItem) -> bool:
        result = self.__check_operator(other, '<')
        if result is not None:
            return result

        return super().__lt__(other)
