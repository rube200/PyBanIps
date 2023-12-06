from ipaddress import AddressValueError, NetmaskValueError, IPv4Network, IPv6Network

IPvNetwork = IPv4Network | IPv6Network


def ip_network(address: int | str | bytes | IPvNetwork, strict=True) -> None | IPvNetwork:
    try:
        return IPv4Network(address, strict)
    except (AddressValueError, NetmaskValueError):
        pass

    try:
        return IPv6Network(address, strict)
    except (AddressValueError, NetmaskValueError):
        pass

    return None
