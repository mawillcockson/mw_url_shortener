from typing import Optional

from pydantic import ConstrainedStr

from mw_url_shortener.settings import defaults

from .base import BaseInDBSchema, BaseSchema


class Username(ConstrainedStr):
    max_length = defaults.max_username_length


class UserBase(BaseSchema):
    username: Optional[Username]


class UserCreate(UserBase):
    username: Username
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase, BaseInDBSchema):
    username: Username


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
