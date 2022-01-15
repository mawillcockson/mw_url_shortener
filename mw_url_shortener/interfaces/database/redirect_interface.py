# mypy: allow_any_expr
from typing import List, Optional

from sqlalchemy import select

from mw_url_shortener.database.models.redirect import RedirectModel
from mw_url_shortener.database.start import AsyncSession, sessionmaker
from mw_url_shortener.schemas.redirect import (
    Redirect,
    RedirectCreate,
    RedirectUpdate,
    random_short_link,
)
from mw_url_shortener.settings import defaults

from .base import DBInterfaceBase


class RedirectDBInterface(
    DBInterfaceBase[Redirect, RedirectCreate, RedirectUpdate],
):
    async def get_by_short_link(
        self, opened_resource: AsyncSession, /, *, short_link: str
    ) -> Optional[Redirect]:
        async with opened_resource.begin():
            redirect_model = (
                await opened_resource.execute(
                    select(RedirectModel).where(RedirectModel.short_link == short_link)
                )
            ).scalar_one_or_none()

            if redirect_model is None:
                return None

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
        id: Optional[int] = None,
        short_link: Optional[str] = None,
        url: Optional[str] = None,
        response_status: Optional[int] = None,
        body: Optional[str] = None,
    ) -> List[Redirect]:
        redirect_schemas: List[Redirect] = []
        query = select(RedirectModel)
        if id is not None:
            query = query.where(RedirectModel.id == id)
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

    async def unique_short_link(
        self,
        opened_resource: AsyncSession,
        /,
        *,
        short_link_length: int = defaults.short_link_length,
    ) -> Optional[str]:
        """
        tries to find a unique short link of the specified length

        if this method returns nothing, it might be time to either
        significantly change the short_link_characters, or change
        short_link_length
        """
        potential_short_links: List[str] = []
        for _ in range(5):
            potential_short_links.append(random_short_link(short_link_length))

        only_matching = select(RedirectModel.short_link).where(
            RedirectModel.short_link.in_(potential_short_links)
        )
        async with opened_resource.begin():
            matching_short_links = (await opened_resource.scalars(only_matching)).all()
        unique_short_links = set(potential_short_links) - set(matching_short_links)
        if unique_short_links:
            return unique_short_links.pop()
        return None


redirect = RedirectDBInterface(RedirectModel, Redirect)
