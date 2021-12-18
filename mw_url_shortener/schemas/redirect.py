import string
from typing import List, Optional

from pydantic import Field, PositiveInt

from mw_url_shortener.settings import defaults
from mw_url_shortener.utils import unsafe_random_string_from_pool

from .base import BaseInDBSchema, BaseSchema


def random_short_link(length: int = defaults.short_link_length) -> str:
    "random short link using allowed characters"
    if length < 1:
        raise ValueError(f"length must be greater than 1, not '{length}'")
    return unsafe_random_string_from_pool(
        length=length, allowed_characters=defaults.short_link_characters
    )


class RedirectBase(BaseSchema):
    short_link: Optional[str] = None
    response_status: Optional[PositiveInt] = None
    url: Optional[str] = None
    body: Optional[str] = None


class RedirectCreate(RedirectBase):
    short_link: str = Field(default_factory=random_short_link)
    response_status: PositiveInt = defaults.redirect_response_status
    url: str = defaults.redirect_url
    body: Optional[str] = defaults.redirect_body


class RedirectUpdate(RedirectBase):
    pass


class RedirectInDBBase(RedirectBase, BaseInDBSchema):
    response_status: PositiveInt
    url: str
    body: str

    class Config:
        orm_mode = True


class Redirect(RedirectInDBBase):
    pass


class RedirectInDB(RedirectInDBBase):
    pass
