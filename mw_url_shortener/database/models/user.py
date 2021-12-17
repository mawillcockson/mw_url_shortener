# mypy: allow_any_expr
from sqlalchemy import Column, Integer, String

from mw_url_shortener.settings import defaults

from .base import DeclarativeBase


class UserModel(DeclarativeBase):
    __tablename__ = "user"

    username = Column(String(defaults.max_username_length), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(username={self.username!r}, hashed_password={self.hashed_password!r})"
