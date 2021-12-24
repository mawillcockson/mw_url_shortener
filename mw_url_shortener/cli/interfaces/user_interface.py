from httpx import AsyncClient

from mw_url_shortener import database_interface
from mw_url_shortener.database.start import sessionmaker

from .base import BaseInterface, ResourceType


class UserInterface(BaseInterface):
    def __init__(self, resource: ResourceType):
        super().__init__(resource)

        if isinstance(resource, sessionmaker):
            self.interface = database_interface.user
        elif isinstance(resource, AsyncClient):
            raise NotImplementedError
        else:
            raise TypeError(f"unkown resource type: '{type(resource)}'")
