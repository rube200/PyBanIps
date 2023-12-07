from ipaddress import IPv4Address
from ipaddress import IPv6Address
from typing import Callable

from PyQt6.QtCore import QObject
from PyQt6.QtGui import QValidator

from utils.ip_address_utils import IPvAddress


def validate_octet(octet: str) -> QValidator.State:
    if not octet:
        return QValidator.State.Intermediate

    if not (octet.isascii() and octet.isdigit()):
        return QValidator.State.Invalid

    octet_len = len(octet)
    if octet_len > 3:
        return QValidator.State.Invalid

    if int(octet, 10) > 255:
        return QValidator.State.Invalid

    return QValidator.State.Acceptable


class AddressValidator(QValidator):
    def __init__(self, parent: QObject, feedback_cb: Callable[[str], None]):
        super().__init__(parent)
        self._feedback_cb = feedback_cb

    def _validate_base_address(self, address: IPvAddress) -> QValidator.State:
        if address.is_global:
            return QValidator.State.Acceptable

        if address.is_private:
            self._feedback_cb and self._feedback_cb('Private addresses are not allowed!')
            return QValidator.State.Intermediate

        if address.is_link_local:
            print(f"link local address: {address}")

        if address.is_loopback:
            print(f"loopback address: {address}")

        if address.is_multicast:
            print(f"multicast address: {address}")

        if address.is_reserved:
            print(f"reserved address: {address}")

        if address.is_unspecified:
            print(f"unspecified address: {address}")

        return QValidator.State.Intermediate

    def _validate_ipv4(self, raw_add: str) -> QValidator.State:
        self._feedback_cb and self._feedback_cb('')
        if ':' in raw_add or '/' in raw_add:
            return QValidator.State.Invalid

        octets = raw_add.split('.')
        octets_len = len(octets)
        if octets_len > 4:
            return QValidator.State.Invalid

        for i in range(octets_len):
            octet = octets[i]
            if not octet and i + 2 == octets_len:
                return QValidator.State.Invalid

            if validate_octet(octet) == QValidator.State.Invalid:
                return QValidator.State.Invalid
        try:
            address = IPv4Address(raw_add)
            return self._validate_base_address(address)
        except ValueError:
            return QValidator.State.Intermediate

    def _validate_ipv6(self, raw_add: str) -> QValidator.State:
        self._feedback_cb and self._feedback_cb('')
        if '/' in raw_add:
            return QValidator.State.Invalid

        if raw_add.count('::') > 1 or ':::' in raw_add:
            return QValidator.State.Invalid

        parts = raw_add.split(':')
        parts_len = len(parts)
        if parts_len > 8:
            return QValidator.State.Invalid

        ipv4_suffix = '.' in parts[-1]
        if ipv4_suffix and parts_len > 7:
            return QValidator.State.Invalid

        hex_set = frozenset('0123456789ABCDEFabcdef')
        for i in range(parts_len - 1 if ipv4_suffix else parts_len):
            hextet = parts[i]
            if not hextet:
                continue

            if not hex_set.issuperset(hextet):
                return QValidator.State.Invalid

            hextet_len = len(hextet)
            if hextet_len > 4:
                return QValidator.State.Invalid

        if ipv4_suffix:
            if self._validate_ipv4(parts[-1]) == QValidator.State.Invalid:
                return QValidator.State.Invalid

        try:
            address = IPv6Address(raw_add)
            return self._validate_base_address(address)
        except ValueError:
            return QValidator.State.Intermediate

    def validate(self, address: str, pos: int) -> (QValidator.State, str, int):
        if not address:
            return QValidator.State.Intermediate, address, pos

        is_ipv4 = self._validate_ipv4(address)
        if is_ipv4 == QValidator.State.Acceptable:
            return QValidator.State.Acceptable, address, pos

        is_ipv6 = self._validate_ipv6(address)
        if is_ipv6 == QValidator.State.Acceptable:
            return QValidator.State.Acceptable, address, pos

        if is_ipv4 == is_ipv6:
            return is_ipv4, address, pos

        return QValidator.State.Intermediate, address, pos

    def get_color(self, address: str) -> str:
        if not address:
            return '#FFFFFF'

        result, _, _ = self.validate(address, 0)
        match result:
            case QValidator.State.Acceptable:
                return '#9BDF9B'
            case QValidator.State.Invalid:
                return '#FF9B9B'
            case _:
                return '#FFFF9B'
