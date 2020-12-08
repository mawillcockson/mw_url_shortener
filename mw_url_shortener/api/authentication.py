print(f"imported mw_url_shortener.api.authentication as {__name__}")
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from ..database.interface import get_user
from ..database.models import User
from .. import HashedPassword, Username, PlainPassword


security = HTTPBasic()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
def authorize(credentials: HTTPBasicCredentials = Depends(security)) -> User:
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
