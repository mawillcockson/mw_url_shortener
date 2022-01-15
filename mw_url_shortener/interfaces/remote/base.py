from enum import Enum
from typing import Dict, Generic, List, Optional, Type, TypeVar, Union

from httpx import AsyncClient, HTTPStatusError, Request, Response

from mw_url_shortener.interfaces.base import (
    CreateSchemaType,
    InterfaceBase,
    ObjectSchemaType,
    UpdateSchemaType,
)


class Endpoint(Enum):
    user = "user"
    redirect = "redirect"


class RemoteInterfaceBase(
    InterfaceBase[
        AsyncClient,
        ObjectSchemaType,
        CreateSchemaType,
        UpdateSchemaType,
    ],
):
    def __init__(self, schema: Type[ObjectSchemaType], endpoint: Endpoint):
        """
        interface object with default methods to create, read, update, delete
        """
        self.schema = schema
        self.endpoint = endpoint.value

    async def get_by_id(
        self, opened_resource: AsyncClient, /, *, id: int
    ) -> Optional[ObjectSchemaType]:
        params = {"id": id}
        async with opened_resource as client:
            response = await client.get(f"/v0/{self.endpoint}/", params=params)
        schema_json = response.text
        if not schema_json:
            return None
        return self.schema.parse_raw(schema_json)

    async def create(
        self,
        opened_resource: AsyncClient,
        /,
        *,
        create_object_schema: CreateSchemaType,
    ) -> Optional[ObjectSchemaType]:
        create_schema_json = create_object_schema.json()
        response = await opened_resource.post(
            f"/v0/{self.endpoint}/", content=create_schema_json.encode("utf-8")
        )
        schema_json = response.text
        if not schema_json:
            return None
        return self.schema.parse_raw(schema_json)

    async def update(
        self,
        opened_resource: AsyncClient,
        /,
        *,
        current_object_schema: ObjectSchemaType,
        update_object_schema: UpdateSchemaType,
    ) -> Optional[ObjectSchemaType]:
        update_data = update_object_schema.dict(exclude_unset=True)
        updated_object = current_object_schema.copy(exclude={"id"}, update=update_data)
        new_object_json = updated_object.json(exclude_none=True)

        if not new_object_json:
            return current_object_schema

        async with opened_resource as client:
            response = await client.put(
                f"/v0/{self.endpoint}/", content=new_object_json.encode("utf-8")
            )
        schema_json = response.text
        return self.schema.parse_raw(schema_json)

    async def remove_by_id(
        self, opened_resource: AsyncClient, /, *, id: int
    ) -> Optional[ObjectSchemaType]:
        params = {"id": id}
        response = await opened_resource.delete(f"/v0/{self.endpoint}/", params=params)
        schema_json = response.text
        if not schema_json:
            return None
        return self.schema.parse_raw(schema_json)
