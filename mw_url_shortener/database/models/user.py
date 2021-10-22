from sqlalchemy import Column, Integer, String

from .base import Base


class User(Base):
    __table__ = "user_table"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
