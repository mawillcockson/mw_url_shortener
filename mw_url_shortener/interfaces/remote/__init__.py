from typing import TYPE_CHECKING

from .authentication import OAuth2PasswordBearerHandler as OAuth2PasswordBearerHandler
from .redirect_interface import redirect as redirect
from .user_interface import user as user

if TYPE_CHECKING:
    import inject
    from httpx import AsyncClient


def inject_async_client(
    binder: "inject.Binder", *, async_client: "AsyncClient"
) -> None:
    binder.bind("AsyncClient", async_client)
