from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import user as user_interface
from mw_url_shortener.schemas.security import AccessToken
from mw_url_shortener.security import make_jwt_token
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
    access_token = make_jwt_token(
        username=authenticated_user.username,
        token_expiration=expiration_date,
        jwt_secret_key=server_settings.jwt_secret_key,
        algorithm=server_settings.jwt_hash_algorithm,
    )
    return access_token


router = APIRouter()
# this is hardcoded here, but the function is added as another endpoint at the
# toplevel FastAPI app in mw_url_shortener.server.cli.make_fastapi_app()
router.post("/token")(login_for_access_token)
