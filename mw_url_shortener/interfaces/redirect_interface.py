from mw_url_shortener.schemas.redirect import Redirect, RedirectCreate, RedirectUpdate

from .base import InterfaceBase, ResourceType


class RedirectInterface(
    InterfaceBase[ResourceType, Redirect, RedirectCreate, RedirectUpdate]
):
    "generic user data interface"
