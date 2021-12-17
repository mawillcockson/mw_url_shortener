from pydantic import BaseModel, Extra


class BaseSchema(BaseModel):
    class Config:
        extra = Extra.ignore


class BaseInDBSchema(BaseSchema):
    id: int
