from pydantic import BaseModel
from ..server.api.authentication import HashedPassword


class Redirect(BaseModel):
    key: str
    url: str


class User(BaseModel):
    username: str
    hashed_password: HashedPassword
