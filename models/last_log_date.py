from datetime import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import CHAR, CheckConstraint
from sqlalchemy.sql.functions import now

from models.database_mode_base import DatabaseModelBase


class LastLogDate(DatabaseModelBase):
    __tablename__ = 'last_load_log'

    lock: Mapped[str] = mapped_column(CHAR(1), CheckConstraint('lock=\'X\''), primary_key=True, server_default='X')
    last_load_date: Mapped[datetime] = mapped_column(server_default=now(), nullable=False)
