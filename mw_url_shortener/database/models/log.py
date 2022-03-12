# mypy: allow_any_expr
from sqlalchemy import Column, Integer, String

from mw_url_shortener.settings import defaults

from .base import DeclarativeBase


class LogModel(DeclarativeBase):
    __tablename__ = "log"

    # len(datetime_obj.isoformat()) == 32
    date_time = Column(String(32), nullable=False)
    event = Column(String(defaults.log_message_max_length), nullable=False)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(date_time={self.date_time!r}, "
            f"event={self.event!r})"
        )
