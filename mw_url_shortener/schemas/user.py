from typing import Optional

from pydantic import ConstrainedStr, Extra

from mw_url_shortener.settings import defaults

from .base import BaseInDBSchema, BaseSchema


class Username(ConstrainedStr):
    min_length = 1
    max_length = defaults.max_username_length


class Password(ConstrainedStr):
    min_length = 1
    max_length = defaults.max_password_length


class UserBase(BaseSchema):
    username: Optional[Username]

    class Config:
        extra = Extra.forbid


class UserCreate(UserBase):
    username: Username
    password: Password


class UserUpdate(UserBase):
    password: Optional[Password] = None


class UserInDBBase(UserBase, BaseInDBSchema):
    username: Username


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
