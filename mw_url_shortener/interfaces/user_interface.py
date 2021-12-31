from typing import List, Optional, Protocol

from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate

from .base import InterfaceBaseProtocol, OpenedResource


class UserInterface(InterfaceBaseProtocol):
    "generic user data interface"

    async def create(
        self, opened_resource: OpenedResource, /, *, create_object_schema: UserCreate
    ) -> User:
        ...

    async def get_by_id(self, opened_resource: OpenedResource, /, *, id: int) -> User:
        ...

    async def update(
        self,
        opened_resource: OpenedResource,
        /,
        *,
        current_object_schema: User,
        update_object_schema: UserUpdate,
    ) -> User:
        ...

    async def search(
        self,
        opened_resource: OpenedResource,
        /,
        *,
        skip: int = 0,
        limit: int = 0,
        id: Optional[int] = None,
        username: Optional[str] = None,
    ) -> List[User]:
        ...
