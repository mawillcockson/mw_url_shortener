# mypy: allow_any_expr
from typing import List, Optional

from httpx import AsyncClient

from mw_url_shortener.schemas.redirect import (
    Redirect,
    RedirectCreate,
    RedirectUpdate,
    random_short_link,
)
from mw_url_shortener.settings import defaults

from ..redirect_interface import RedirectInterface
from .base import RemoteInterfaceBase


class RedirectRemoteInterface(
    RemoteInterfaceBase[Redirect, RedirectCreate, RedirectUpdate],
    RedirectInterface[AsyncClient],
):
    pass


redirect = RedirectRemoteInterface(Redirect)
