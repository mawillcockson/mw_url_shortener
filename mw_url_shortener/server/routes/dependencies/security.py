# mypy: allow_any_expr
from typing import Optional

import inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import user as user_interface
from mw_url_shortener.schemas.user import User
from mw_url_shortener.server.settings import ServerSettings

from .main import get_async_session, get_server_settings

# this is actually set in mw_url_shortener.server.cli.make_fastapi_app()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    async_session: AsyncSession = Depends(get_async_session),
    token: str = Depends(oauth2_scheme),
    server_settings: ServerSettings = Depends(get_server_settings),
) -> User:
    try:
        decoded = jwt.decode(
            token,
            server_settings.jwt_secret_key,
            algorithms=server_settings.jwt_hash_algorithm,
        )
    except JWTError as err:
        raise credentials_exception from err

    username = decoded.get("sub")
    authenticated_user = await user_interface.get_by_username(
        async_session, username=username
    )
    if authenticated_user is None:
        raise credentials_exception
    return authenticated_user
