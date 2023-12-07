from datetime import datetime

from sqlalchemy import CHAR
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from models.database_mode_base import DatabaseModelBase


class LastLogDate(DatabaseModelBase):
    __tablename__ = 'last_load_log'

    lock: Mapped[str] = mapped_column(CHAR(1), CheckConstraint('lock=\'X\''), primary_key=True, server_default='X')
    last_load_date: Mapped[datetime] = mapped_column(nullable=False)
