from enum import Enum
from typing import Dict, Generic, List, Optional, Type, TypeVar, Union

from httpx import AsyncClient, HTTPStatusError, Request, Response
from pydantic import parse_raw_as

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
        response = await opened_resource.get(f"v0/{self.endpoint}/", params=params)

        schema_type = self.schema
        object_schemas = parse_raw_as(List[schema_type], response.text)  # type: ignore

        assert (
            len(object_schemas) == 1
        ), f"got more than one {self.endpoint} with the same id: {object_schemas}"

        object_schema = object_schemas[0]

        return object_schema

    async def create(
        self,
        opened_resource: AsyncClient,
        /,
        *,
        create_object_schema: CreateSchemaType,
    ) -> Optional[ObjectSchemaType]:
        create_schema_json = create_object_schema.json()
        response = await opened_resource.post(
            f"v0/{self.endpoint}/", content=create_schema_json.encode("utf-8")
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
        current_schema_json = current_object_schema.json()
        update_schema_json = update_object_schema.json()
        # NOTE:FUTURE partial serialization would allow for serializing
        # pydantic.BaseModels into an object that json.dumps can encode, and
        # can thus be included in other arbitrary data, like a list
        # https://github.com/samuelcolvin/pydantic/issues/951
        update_body = (
            "{"
            f'"current_object_schema":{current_schema_json},'
            f'"update_object_schema":{update_schema_json}'
            "}"
        )
        response = await opened_resource.put(
            f"v0/{self.endpoint}/", content=update_body.encode("utf-8")
        )
        schema_json = response.text
        return self.schema.parse_raw(schema_json)

    async def remove_by_id(
        self, opened_resource: AsyncClient, /, *, id: int
    ) -> Optional[ObjectSchemaType]:
        params = {"id": id}
        response = await opened_resource.delete(f"v0/{self.endpoint}/", params=params)
        schema_json = response.text
        if not schema_json:
            return None
        return self.schema.parse_raw(schema_json)
