print(f"imported mw_url_shortener.database.models as {__name__}")
from pydantic import BaseModel, Field, AnyUrl
from ..types import HashedPassword, Username, Key, Uri
from ..utils import orjson_dumps, orjson_loads, unsafe_random_chars


def key_factory() -> Key:
    "Makes a key that is an appropriate length"
    raise NotImplementedError(f"Don't know where to get the currently set KEY_LENGTH from yet")
    # return Key(unsafe_random_chars(KEY_LENGTH))


class RedirectModel(BaseModel):
    key: Key = Field(default_factory=key_factory)
    # NOTE:BUG should use pydantic.AnyUrl, or modify it to include data URIs
    # https://pydantic-docs.helpmanual.io/usage/types/#urls
    uri: Uri

    class Config:
        orm_mode = True
        # NOTE: Supposed to help speed up JSON encoding and decoding
        # from:
        # https://pydantic-docs.helpmanual.io/usage/exporting_models/#custom-json-deserialisation
        json_loads = orjson_loads
        json_dumps = orjson_dumps
        allow_mutation = False


class UserModel(BaseModel):
    username: Username
    hashed_password: HashedPassword

    class Config:
        orm_mode = True
        json_loads = orjson_loads
        json_dumps = orjson_dumps
        allow_mutation = False
