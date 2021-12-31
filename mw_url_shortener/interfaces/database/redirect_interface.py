# mypy: allow_any_expr
from typing import List, Optional

from sqlalchemy import select

from mw_url_shortener.database.models.redirect import RedirectModel
from mw_url_shortener.database.start import AsyncSession, sessionmaker
from mw_url_shortener.schemas.redirect import Redirect, RedirectCreate, RedirectUpdate

from ..redirect_interface import RedirectInterface
from .base import DBInterfaceBase


class RedirectDBInterface(
    DBInterfaceBase[Redirect, RedirectCreate, RedirectUpdate],
    RedirectInterface[AsyncSession],
):
    async def get_by_short_link(
        self, opened_resource: AsyncSession, /, *, short_link: str
    ) -> Redirect:
        async with opened_resource.begin():
            redirect_model = (
                await opened_resource.execute(
                    select(RedirectModel).where(RedirectModel.short_link == short_link)
                )
            ).scalar_one()

            assert isinstance(
                redirect_model, RedirectModel
            ), f"expected '{RedirectModel}', got '{type(redirect_model)}'"

            return self.schema.from_orm(redirect_model)

    async def search(
        self,
        opened_resource: AsyncSession,
        /,
        *,
        skip: int = 0,
        limit: int = 100,
        short_link: Optional[str] = None,
        url: Optional[str] = None,
        response_status: Optional[int] = None,
        body: Optional[str] = None,
    ) -> List[Redirect]:
        redirect_schemas: List[Redirect] = []
        query = select(RedirectModel)
        if short_link is not None:
            query = query.where(RedirectModel.short_link == short_link)
        if url is not None:
            query = query.where(RedirectModel.url == url)
        if response_status is not None:
            query = query.where(RedirectModel.response_status == response_status)
        if body is not None:
            query = query.where(RedirectModel.body == body)

        query = query.offset(skip).limit(limit).order_by(RedirectModel.id)
        async with opened_resource.begin():
            redirect_models = (await opened_resource.scalars(query)).all()
            for redirect_model in redirect_models:
                redirect_schemas.append(self.schema.from_orm(redirect_model))
        return redirect_schemas


redirect = RedirectDBInterface(RedirectModel, Redirect)
