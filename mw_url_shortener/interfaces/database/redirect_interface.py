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
    RedirectInterface["sessionmaker[AsyncSession]"],
):
    async def get_by_short_link(
        self, async_session: AsyncSession, *, short_link: str
    ) -> Redirect:
        async with async_session.begin():
            redirect_model = (
                await async_session.execute(
                    select(RedirectModel).where(RedirectModel.short_link == short_link)
                )
            ).scalar_one()

            assert isinstance(
                redirect_model, RedirectModel
            ), f"expected '{RedirectModel}', got '{type(redirect_model)}'"

            return self.schema.from_orm(redirect_model)

    async def get_by_url(
        self, async_session: AsyncSession, *, url: str
    ) -> List[Redirect]:
        redirect_schemas: List[Redirect] = []
        select_by_url = (
            select(RedirectModel)
            .where(RedirectModel.url == url)
            .order_by(RedirectModel.id)
        )
        async with async_session.begin():
            redirect_models = (await async_session.scalars(select_by_url)).all()
            for redirect_model in redirect_models:
                redirect_schemas.append(self.schema.from_orm(redirect_model))
        return redirect_schemas

    async def get_by_response_status(
        self, async_session: AsyncSession, *, response_status: int
    ) -> List[Redirect]:
        redirect_schemas: List[Redirect] = []
        select_by_response_status = (
            select(RedirectModel)
            .where(RedirectModel.response_status == response_status)
            .order_by(RedirectModel.id)
        )
        async with async_session.begin():
            redirect_models = (
                await async_session.scalars(select_by_response_status)
            ).all()
            for redirect_model in redirect_models:
                redirect_schemas.append(self.schema.from_orm(redirect_model))
        return redirect_schemas

    async def get_by_body(
        self, async_session: AsyncSession, *, body: str
    ) -> List[Redirect]:
        redirect_schemas: List[Redirect] = []
        select_by_body = (
            select(RedirectModel)
            .where(RedirectModel.body == body)
            .order_by(RedirectModel.id)
        )
        async with async_session.begin():
            redirect_models = (await async_session.scalars(select_by_body)).all()
            for redirect_model in redirect_models:
                redirect_schemas.append(self.schema.from_orm(redirect_model))
        return redirect_schemas

    async def search(
        self,
        async_session: AsyncSession,
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
        async with async_session.begin():
            redirect_models = (await async_session.scalars(query)).all()
            for redirect_model in redirect_models:
                redirect_schemas.append(self.schema.from_orm(redirect_model))
        return redirect_schemas


redirect = RedirectDBInterface(RedirectModel, Redirect)
