from sqlalchemy import Column, Integer, String

from .base import DeclarativeBase
from mw_url_shortener.settings import defaults


class UserModel(DeclarativeBase):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(defaults.max_username_length), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
