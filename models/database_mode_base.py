from sqlalchemy.orm import DeclarativeBase

from sql_types.address_type import AddressType
from sql_types.network_type import NetworkType


class DatabaseModelBase(DeclarativeBase):
    type_annotation_map = {
        AddressType: AddressType,
        NetworkType: NetworkType,
    }
