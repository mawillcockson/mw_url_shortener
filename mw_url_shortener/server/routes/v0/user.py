from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import user as user_interface
from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate

from ..dependencies import get_async_session, get_current_user


async def get_by_id(
    id: int,
    async_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> User:
    retrieved_user = await user_interface.get_by_id(async_session, id=id)
    if retrieved_user is not None:
        return retrieved_user

    raise HTTPException(status_code=404, detail="could not find user")


async def create(
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


async def update(
    current_object_schema: User,
    update_object_schema: UserUpdate,
    async_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> User:
    updated_user = await user_interface.update(
        async_session,
        current_object_schema=current_object_schema,
        update_object_schema=update_object_schema,
    )
    if updated_user is not None:
        return updated_user

    raise HTTPException(status_code=409, detail="could not update user")


router = APIRouter()
router.get("/me")(me)
router.get("/")(get_by_id)
router.post("/")(create)
router.put("/")(update)
