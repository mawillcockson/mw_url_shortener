# mypy: allow_any_expr
"""
all of the authentication and authorization helper functions
"""
from datetime import datetime, timedelta
from typing import cast

from jose import jwt
from passlib.context import CryptContext

from mw_url_shortener.schemas.security import AccessToken

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    hashed_password = password_context.hash(password)
    if not isinstance(hashed_password, str):
        raise TypeError(f"expected str, instead got '{type(hashed_password)}'")
    return hashed_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    is_valid = password_context.verify(plain_password, hashed_password)
    if not isinstance(is_valid, bool):
        raise TypeError(f"expected bool, instead got '{type(is_valid)}'")
    return bool(is_valid)


def make_jwt_token(
    username: str, token_valid_duration: timedelta, jwt_secret_key: str, algorithm: str
) -> AccessToken:
    expiration_date = datetime.utcnow() + token_valid_duration
    token_data = {"sub": username, "exp": expiration_date}
    encoded_token: str = jwt.encode(
        token_data,
        jwt_secret_key,
        algorithm=algorithm,
    )
    return AccessToken(access_token=encoded_token)
