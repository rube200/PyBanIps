from sqlalchemy.orm import Mapped, mapped_column

from models.address_network_base import AddressNetworkBase
from models.database_mode_base import DatabaseModelBase
from sql_types.address_type import AddressType
from utils.ip_address_utils import IPvAddress


class AnalyseAddress(AddressNetworkBase, DatabaseModelBase):
    __tablename__ = 'addresses'

    ip: Mapped[AddressType] = mapped_column(primary_key=True)
    count: Mapped[int] = mapped_column(server_default='1', nullable=False)

    def __init__(self, ip: IPvAddress):
        super().__init__()
        self.ip = ip

        # noinspection PyTypeChecker
        self.count = 1

    def __repr__(self) -> str:
        return f'{self.ip!s} - {self.count!r}'

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        return super().__ne__(other)
