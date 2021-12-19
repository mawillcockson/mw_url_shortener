# mypy: allow_any_expr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener.database.models.redirect import RedirectModel
from mw_url_shortener.schemas.redirect import Redirect, RedirectCreate, RedirectUpdate
from typing import List

from .base import InterfaceBase


class InterfaceRedirect(
    InterfaceBase[RedirectModel, Redirect, RedirectCreate, RedirectUpdate]
):
    async def get_by_short_link(
        self, async_session: AsyncSession, *, short_link: str
    ) -> Redirect:
        async with async_session.begin():
            redirect_model = (
                await async_session.execute(
                    select(self.model).where(self.model.short_link == short_link)
                )
            ).scalar_one()

            assert isinstance(
                redirect_model, self.model
            ), f"expected '{self.model}', got '{type(redirect_model)}'"

            return self.schema.from_orm(redirect_model)

    async def get_by_url(self, async_session: AsyncSession, *, url: str) -> List[Redirect]:
        redirect_schemas: List[Redirect] = []
        select_by_url = select(self.model).where(self.model.url == url).order_by(self.model.id)
        async with async_session.begin():
            redirect_models = (await async_session.scalars(select_by_url)).all()
            for redirect_model in redirect_models:
                redirect_schemas.append(self.schema.from_orm(redirect_model))
        return redirect_schemas


redirect = InterfaceRedirect(RedirectModel, Redirect)
