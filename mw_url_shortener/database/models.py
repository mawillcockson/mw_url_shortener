print(f"imported mw_url_shortener.database.models as {__name__}")
from pydantic import BaseModel, Field, AnyUrl
from .. import HashedPassword, Username, Key, Uri
from ..random_chars import unsafe_random_chars


def key_factory() -> Key:
    "Makes a key that is an appropriate length"
    raise NotImplementedError(f"Don't know where to get the currently set KEY_LENGTH from yet")
    # return Key(unsafe_random_chars(KEY_LENGTH))


class Redirect(BaseModel):
    key: Key = Field(default_factory=key_factory, min_length=1)
    # NOTE:BUG should use pydantic.AnyUrl, or modify it to include data URIs
    # https://pydantic-docs.helpmanual.io/usage/types/#urls
    uri: Uri = Field(..., min_length=1)

    class Config:
        orm_mode = True


class User(BaseModel):
    username: Username
    hashed_password: HashedPassword

    class Config:
        orm_mode = True
