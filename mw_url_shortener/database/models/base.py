# mypy: allow_any_expr
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class DeclarativeBase:
    "base class for ORM models"
    id = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        model_attributes = {key: getattr(self, key) for key in self.__table__.c.keys()}
        stringified = [f"{key}={value!r}" for key, value in model_attributes.items()]
        return f"{self.__class__.__name__}({', '.join(stringified)})"
