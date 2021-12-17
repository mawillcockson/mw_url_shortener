from pydantic import BaseModel


class BaseSchema(BaseModel):
    pass


class BaseInDBSchema(BaseSchema):
    id: int
