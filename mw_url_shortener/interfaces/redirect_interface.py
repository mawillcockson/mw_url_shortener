from mw_url_shortener.schemas.redirect import Redirect, RedirectCreate, RedirectUpdate

from .base import InterfaceBase, ResourceT


class RedirectInterface(
    InterfaceBase[ResourceT, Redirect, RedirectCreate, RedirectUpdate]
):
    "generic user data interface"
