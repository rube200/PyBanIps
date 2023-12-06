from sqlalchemy.orm import Mapped, mapped_column

from models.address_network_base import AddressNetworkBase
from models.database_mode_base import DatabaseModelBase
from sql_types.address_type import AddressType
from sql_types.network_type import NetworkType
from utils.ip_address_utils import IPvAddress
from utils.ip_network_utils import IPvNetwork


class BannedNetwork(AddressNetworkBase, DatabaseModelBase):
    __tablename__ = 'bans'

    ip: Mapped[NetworkType] = mapped_column(primary_key=True)

    def __contains__(self, item: object) -> bool:
        if isinstance(item, AddressNetworkBase):
            item = item.ip

        if isinstance(item, AddressType | NetworkType | IPvAddress | IPvNetwork):
            if self.ip.version != item.version:
                return False

            if isinstance(item, NetworkType | IPvNetwork):
                return self.ip.supernet_of(item)

        return item in self.ip

    def __repr__(self) -> str:
        return f'{self.ip!s} - {self.date!s}'
