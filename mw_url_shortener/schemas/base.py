from typing import Optional

from pydantic import BaseModel


class BaseSchema(BaseModel):
    pass


class BaseInDBSchema(BaseSchema):
    id: Optional[int] = None
