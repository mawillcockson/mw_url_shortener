# mypy: allow_any_expr
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import user as user_interface
from mw_url_shortener.schemas.security import AccessToken
from mw_url_shortener.server.settings import ServerSettings

from ..dependencies import credentials_exception, get_async_session, get_server_settings


async def login_for_access_token(
    async_session: AsyncSession = Depends(get_async_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
    server_settings: ServerSettings = Depends(get_server_settings),
) -> AccessToken:
    username = form_data.username
    password = form_data.password
    authenticated_user = await user_interface.authenticate(
        async_session, username=username, password=password
    )
    if authenticated_user is None:
        raise credentials_exception
    expiration_date = (
        datetime.utcnow() + server_settings.jwt_access_token_valid_duration
    )
    token_data = {"sub": authenticated_user.username, "exp": expiration_date}
    encoded_token: str = jwt.encode(
        token_data,
        server_settings.jwt_secret_key,
        algorithm=server_settings.jwt_hash_algorithm,
    )
    print(encoded_token)
    return AccessToken(access_token=encoded_token)


router = APIRouter()
router.post("/token")(login_for_access_token)
