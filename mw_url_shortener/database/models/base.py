# mypy: allow_any_expr
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class DeclarativeBase:
    "base class for ORM models"
    id = Column(Integer, primary_key=True)
