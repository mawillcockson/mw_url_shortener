from typing import Generic, TypeVar

from mw_url_shortener.schemas.base import BaseInDBSchema, BaseSchema

ObjectSchemaType = TypeVar("ObjectSchemaType", bound=BaseInDBSchema)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class InterfaceBase(Generic[ObjectSchemaType, CreateSchemaType, UpdateSchemaType]):
    "generic base interface for abstracting database and api access"
