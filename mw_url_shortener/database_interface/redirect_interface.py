# mypy: allow_any_expr
from mw_url_shortener.database.models.redirect import RedirectModel
from mw_url_shortener.schemas.redirect import Redirect, RedirectCreate, RedirectUpdate

from .base import InterfaceBase


class InterfaceRedirect(
    InterfaceBase[RedirectModel, Redirect, RedirectCreate, RedirectUpdate]
):
    pass


redirect = InterfaceRedirect(RedirectModel, Redirect)
