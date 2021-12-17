from typing import Optional

from pydantic import BaseModel as BaseSchema
from pydantic import ConstrainedStr

from mw_url_shortener.settings import defaults


class Username(ConstrainedStr):
    max_length = defaults.max_username_length


class UserBase(BaseSchema):
    username: Optional[Username]


class UserCreate(UserBase):
    username: Username
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None
    username: Username

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
