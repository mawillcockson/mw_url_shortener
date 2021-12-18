# mypy: allow_any_expr
from sqlalchemy import Column, Integer, String

from mw_url_shortener.settings import defaults

from .base import DeclarativeBase


class RedirectModel(DeclarativeBase):
    __tablename__ = "redirect"

    short_link = Column(String, unique=True, nullable=False)
    response_status = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    body = Column(String, nullable=True)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"response_status={self.response_status}, "
            f"url={self.url!r}. body={self.body!r})"
        )
