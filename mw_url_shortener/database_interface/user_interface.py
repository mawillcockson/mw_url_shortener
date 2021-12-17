# mypy: allow_any_expr
from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mw_url_shortener.database.models.user import UserModel
from mw_url_shortener.database_interface.base import InterfaceBase
from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate
from mw_url_shortener.security import hash_password, verify_password


class InterfaceUser(InterfaceBase[UserModel, User, UserCreate, UserUpdate]):
    async def get_by_username(
        self, async_session: AsyncSession, *, username: str
    ) -> Optional[User]:
        async with async_session.begin():
            user_model = (
                await async_session.execute(
                    select(UserModel).where(UserModel.username == username)
                )
            ).scalar_one_or_none()
            if user_model is None:
                return None
            assert isinstance(
                user_model, UserModel
            ), f"expected '{UserModel}', got '{type(user_model)}'"
            return self.schema.from_orm(user_model)

    async def create(
        self,
        async_session: AsyncSession,
        *,
        create_object_schema: Union[User, UserCreate],
    ) -> User:
        if hasattr(create_object_schema, "password"):
            password = create_object_schema.password
            create_data = create_object_schema.dict(exclude={"password"})
            create_data["hashed_password"] = hash_password(password)
        else:
            create_data = create_object_schema.dict()

        new_user_schema = User.parse_obj(create_data)
        return await super().create(async_session, create_object_schema=new_user_schema)


    async def update(
        self,
        async_session: AsyncSession,
        *,
        current_object_schema: User,
        object_update_schema: UserUpdate,
    ) -> User:
        if object_update_schema.password is not None:
            hashed_password = hash_password(object_update_schema.password)
            current_object_schema = current_object_schema.copy(
                update={"hashed_password": hashed_password}
            )
            object_update_schema = object_update_schema.copy(exclude={"password"})

        return await super().update(
            async_session,
            current_object_schema=current_object_schema,
            object_update_schema=object_update_schema,
        )

    async def authenticate(
        self, async_session: AsyncSession, *, username: str, password: str
    ) -> Optional[User]:
        async with async_session.begin():
            user_model = (
                await async_session.execute(
                    select(UserModel).where(UserModel.username == username)
                )
            ).scalar_one_or_none()
            if user_model is None:
                return None
            if not verify_password(password, user_model.hashed_password):
                return None
            return self.schema.from_orm(user_model)


user = InterfaceUser(UserModel, User)
