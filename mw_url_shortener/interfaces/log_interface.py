from abc import abstractmethod
from typing import List, Optional, Protocol, runtime_checkable

from mw_url_shortener.schemas.log import Log, LogCreate

from .base import ContravariantOpenedResourceT, InterfaceBaseProtocol


@runtime_checkable
class LogInterface(
    InterfaceBaseProtocol[ContravariantOpenedResourceT, Log, LogCreate],
    Protocol[ContravariantOpenedResourceT],
):
    "generic log data interface"

    @abstractmethod
    async def search(
        self,
        opened_resource: ContravariantOpenedResourceT,
        /,
        *,
        skip: int = 0,
        limit: int = 0,
        id: Optional[int] = None,
    ) -> List[Log]:
        raise NotImplementedError
