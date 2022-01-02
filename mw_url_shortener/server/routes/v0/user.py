from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import user as user_interface
from mw_url_shortener.schemas.user import User, UserCreate

from ..dependencies import get_async_session

# from ..dependencies import get_current_user


async def create_user(
    *,
    async_session: AsyncSession = Depends(get_async_session),
    create_user_schema: UserCreate,
    # current_user: User = Depends(get_current_user)
) -> User:
    created_user = await user_interface.create(
        async_session, create_object_schema=create_user_schema
    )
    if created_user is not None:
        return created_user

    raise HTTPException(status_code=409, detail="could not create user")


router = APIRouter()
router.post("/")(create_user)
