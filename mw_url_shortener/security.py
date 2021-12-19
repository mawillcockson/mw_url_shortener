# mypy: allow_any_expr
"""
all of the authentication and authorization helper functions
"""
from typing import cast

from passlib.context import CryptContext

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
