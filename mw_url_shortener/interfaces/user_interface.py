from typing import List, Optional, Protocol, runtime_checkable

from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate

from .base import ContravariantOpenedResourceT, InterfaceBaseProtocol


@runtime_checkable
class UserInterface(
    InterfaceBaseProtocol[ContravariantOpenedResourceT, User, UserCreate, UserUpdate],
    Protocol[ContravariantOpenedResourceT],
):
    "generic user data interface"

    async def search(
        self,
        opened_resource: ContravariantOpenedResourceT,
        /,
        *,
        skip: int = 0,
        limit: int = 0,
        id: Optional[int] = None,
        username: Optional[str] = None,
    ) -> List[User]:
        ...

    async def authenticate(
        self,
        opened_resource: ContravariantOpenedResourceT,
        /,
        *,
        username: str,
        password: str,
    ) -> Optional[User]:
        ...
