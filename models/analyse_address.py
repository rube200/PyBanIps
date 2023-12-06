from sqlalchemy.orm import Mapped, mapped_column

from models.address_network_base import AddressNetworkBase
from models.database_mode_base import DatabaseModelBase
from sql_types.address_type import AddressType


class AnalyseAddress(AddressNetworkBase, DatabaseModelBase):
    __tablename__ = 'addresses'

    ip: Mapped[AddressType] = mapped_column(primary_key=True)
    count: Mapped[int] = mapped_column(server_default='1', nullable=False)

    def __repr__(self) -> str:
        return f'{self.ip!s} - {self.count!r}'
