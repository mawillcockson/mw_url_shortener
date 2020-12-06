from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from typing import NewType
from ..database.interface import get_user
from ..database.models import UserModel


security = HTTPBasic()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# DONE:NOTE:IMPLEMENTATION Should these be pydantic models instead?
# This would allow the password hashes to be validated, but passlib already
# checks this when they're used.
# A model can't be used for the PlainPassword since the password can be
# anything, including something that looks exactly like a password hash
# DONE:
# Type checking should be sufficient for making sure a PlainPassword never ends
# up in the wrong spot
HashedPassword = NewType("HashedPassword", str)
PlainPassword = NewType("PlainPassword", str)


def verify_password(plain_password: PlainPassword, hashed_password: HashedPassword) -> bool:
    """
    Checks if a password is valid

    Hashes the plaintext password and compares that to the correct hash

    \f
    Copied from:
    https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#hash-and-verify-the-passwords
    """
    return password_context.verify(plain_password, hashed_password)


def hash_password(plain_password: PlainPassword) -> HashedPassword:
    "Hashes a password with the current password context"
    return password_context.hash(plain_password)


# DONE:NOTE:FEATURE::SECURITY Apparently needs password hashing with salt
# DONE:
# The passlib module's CryptContext automatically creates salts and adds them
# to the password hash as needed
def authorize(credentials: HTTPBasicCredentials = Depends(security)) -> UserModel:
    """
    A function that can be used as FastAPI dependency to ensure use of an API
    endpoint is authenticaed

    \f
    Copied from:
    https://fastapi.tiangolo.com/advanced/security/http-basic-auth/#check-the-username
    """
    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    user = get_user(credentials.username)
    if not user:
        raise authentication_error

    if not verify_password(plain_password=credentials.password, hashed_password=user.hashed_password):
        raise authentication_error

    return credentials.username
