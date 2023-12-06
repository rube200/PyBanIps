from datetime import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.functions import now

from sql_types.address_type import AddressType
from sql_types.network_type import NetworkType
from utils.ip_address_utils import IPvAddress
from utils.ip_network_utils import IPvNetwork


class AddressNetworkBase:
    date: Mapped[datetime] = mapped_column(server_default=now(), nullable=False, onupdate=now())

    @property
    def ip(self) -> Mapped[AddressType] | Mapped[NetworkType]:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False

        if isinstance(other, AddressNetworkBase):
            return self.ip.version == other.ip.version and self.ip == other.ip

        if isinstance(other, AddressType | NetworkType | IPvAddress | IPvNetwork):
            # noinspection PyUnresolvedReferences
            return self.ip.version == other.version and self.ip == other

        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        return not self == other
