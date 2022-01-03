from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import user as user_interface
from mw_url_shortener.schemas.user import User, UserCreate

from ..dependencies import get_async_session, get_current_user


async def create_user(
    create_user_schema: UserCreate,
    async_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> User:
    created_user = await user_interface.create(
        async_session, create_object_schema=create_user_schema
    )
    if created_user is not None:
        return created_user

    raise HTTPException(status_code=409, detail="could not create user")


async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


router = APIRouter()
router.get("/me")(me)
router.post("/")(create_user)
