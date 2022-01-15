from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from mw_url_shortener.database.start import AsyncSession
from mw_url_shortener.interfaces.database import user as user_interface
from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate

from ..dependencies import get_async_session, get_current_user


# NOTE:TEST
async def check_authentication(
    username: str,
    password: str,
    async_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Optional[User]:
    authenticated_user = await user_interface.authenticate(
        async_session, username=username, password=password
    )
    return authenticated_user


async def search(
    skip: int = 0,
    limit: int = 100,
    id: Optional[int] = None,
    username: Optional[str] = None,
    async_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> List[User]:
    retrieved_users = await user_interface.search(
        async_session, skip=skip, limit=limit, id=id, username=username
    )
    return retrieved_users


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


async def remove(
    id: int,
    async_session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> User:
    removed_user = await user_interface.remove_by_id(async_session, id=id)
    if removed_user is not None:
        return removed_user

    raise HTTPException(status_code=404, detail="could not remove user")


router = APIRouter()
router.post("/check_authentication")(check_authentication)
router.get("/me")(me)
router.get("/")(search)
router.post("/")(create)
router.put("/")(update)
router.delete("/")(remove)
