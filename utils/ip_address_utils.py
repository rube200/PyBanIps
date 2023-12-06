from ipaddress import AddressValueError, NetmaskValueError, IPv4Address, IPv6Address

IPvAddress = IPv4Address | IPv6Address


def ip_address(address: int | str | bytes | IPvAddress) -> None | IPvAddress:
    try:
        return IPv4Address(address)
    except (AddressValueError, NetmaskValueError):
        pass

    try:
        return IPv6Address(address)
    except (AddressValueError, NetmaskValueError):
        pass

    return None
