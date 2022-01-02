from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import user as user_interface
from mw_url_shortener.schemas.user import User, UserCreate

from ..dependencies import get_async_session

# from ..dependencies import get_current_user

router = APIRouter()


@router.post("/")
async def create_user(
    *,
    async_session: AsyncSession = Depends(get_async_session),
    create_user_schema: UserCreate,
    # current_user: User = Depends(get_current_user)
) -> User:
    return await user_interface.create(
        async_session, create_object_schema=create_user_schema
    )
