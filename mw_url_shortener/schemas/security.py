from datetime import datetime
from typing import TypedDict

from .base import BaseSchema


class AccessToken(BaseSchema):
    access_token: str
    token_type: str = "bearer"


class JWTToken(BaseSchema):
    sub: str
    exp: datetime


class AuthorizationHeaders(TypedDict):
    Authorization: str


class OAuth2PasswordRequestFormData(TypedDict):
    username: str
    password: str


def make_authorization_headers(token: str) -> AuthorizationHeaders:
    return AuthorizationHeaders(Authorization="Bearer" + " " + token)
