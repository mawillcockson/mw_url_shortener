from httpx import AsyncClient

from .interfaces import get_resource


def get_async_client() -> AsyncClient:
    resource = get_resource()
    assert isinstance(
        resource, AsyncClient
    ), f"expected resource to be AsyncClient, got {type(resource)} '{resource}'"
    return resource
