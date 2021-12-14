from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener.database.models.user import UserModel
from mw_url_shortener.database_interface.base import InterfaceBase
from mw_url_shortener.schemas.user import UserCreate, UserUpdate
from mw_url_shortener.security import hash_password, verify_password


class InterfaceUser(InterfaceBase[UserModel, UserCreate, UserUpdate]):
    async def get_by_username(
        self, async_session: AsyncSession, *, username: str
    ) -> Optional[UserModel]:
        async with async_session() as session:
            async with session.begin():
                user_model = (
                    await session.execute(
                        select(UserModel).where(UserModel.username == username)
                    )
                ).scalar_one_or_none()
            if user_model is not None:
                await session.refresh(user_model)
        return user_model

    async def create(
        self, async_session: AsyncSession, *, object_schema_in: UserCreate
    ) -> UserModel:
        object_model = UserModel(
            username=object_schema_in.username,
            hashed_password=hash_password(object_schema_in.password),
        )
        async with async_session() as session:
            async with session.begin():
                session.add(object_model)
            await session.refresh(object_model)
        return object_model

    async def update(
        self,
        async_session: AsyncSession,
        *,
        current_object_model: UserModel,
        object_update_schema: Union[UserUpdate, Dict[str, Any]]
    ) -> UserModel:
        if isinstance(object_update_schema, dict):
            updated_object_data = object_update_schema
        else:
            updated_object_data = object_update_schema.dict(exclude_unset=True)

        if updated_object_data["password"] is not None:
            hashed_password = hash_password(updated_object_data["password"])
            del updated_object_data["password"]
            updated_object_data["hashed_password"] = hashed_password

        return await super().update(
            async_session,
            current_object_model=current_object_model,
            object_update_schema=updated_object_data,
        )

    async def authenticate(
        self, async_session: AsyncSession, *, username: str, password: str
    ) -> Optional[UserModel]:
        user_model = await self.get_by_username(async_session, username=username)
        if user_model is None:
            return None
        if not verify_password(password, user_model.hashed_password):
            return None
        return user_model


user = InterfaceUser(UserModel)
