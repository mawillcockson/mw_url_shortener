from typing import Optional

from pydantic import BaseModel as BaseSchema
from pydantic import constr

from mw_url_shortener.settings import defaults

Username = constr(max_length=defaults.max_username_length)


class UserBase(BaseSchema):
    username: Username


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    username: Optional[Username]
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int]

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str
