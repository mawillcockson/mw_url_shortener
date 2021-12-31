from mw_url_shortener.schemas.redirect import Redirect, RedirectCreate, RedirectUpdate

from .base import InterfaceBase, Resource


class RedirectInterface(
    InterfaceBase[Resource, Redirect, RedirectCreate, RedirectUpdate]
):
    "generic user data interface"
