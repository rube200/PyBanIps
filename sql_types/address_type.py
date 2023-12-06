from typing import Any

from sqlalchemy import types

from utils.ip_address_utils import ip_address, IPvAddress


class AddressType(types.TypeDecorator):
    impl = types.Unicode(50)
    cache_ok = True

    def __init__(self, max_length=50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.impl = types.Unicode(max_length)

    def process_bind_param(self, value: IPvAddress, dialect) -> None | str:
        if value is None:
            return None

        return str(value)

    def process_result_value(self, value: Any, dialect) -> IPvAddress:
        if value is None:
            return None

        return ip_address(str(value))

    @property
    def python_type(self) -> property:
        return type(self.impl).python_type
