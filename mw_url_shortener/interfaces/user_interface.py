from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate

from .base import InterfaceBase, ResourceType


class UserInterface(InterfaceBase[ResourceType, User, UserCreate, UserUpdate]):
    "generic user data interface"
