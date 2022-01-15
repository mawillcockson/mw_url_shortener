from typing import Dict, Generic, List, Optional, Type, TypeVar, Union

from httpx import AsyncClient, HTTPStatusError, Request, Response

from mw_url_shortener.interfaces.base import (
    CreateSchemaType,
    InterfaceBase,
    ObjectSchemaType,
    UpdateSchemaType,
)


class RemoteInterfaceBase(
    InterfaceBase[
        AsyncClient,
        ObjectSchemaType,
        CreateSchemaType,
        UpdateSchemaType,
    ],
):
    def __init__(self, schema: Type[ObjectSchemaType]):
        """
        interface object with default methods to create, read, update, delete
        """
        self.schema = schema

    async def get_by_id(
        self, opened_resource: AsyncClient, /, *, id: int
    ) -> Optional[ObjectSchemaType]:
        params = {"id": id}
        async with opened_resource as client:
            response = await client.get("/v0/user/", params=params)
        schema_json = response.text
        if not schema_json:
            return None
        return self.schema.parse_raw(schema_json)
