from datetime import datetime

from .base import BaseSchema


class AccessToken(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class JWTToken(BaseSchema):
    sub: str
    exp: datetime
