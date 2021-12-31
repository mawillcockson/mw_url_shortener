# mypy: allow_any_expr
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select

from mw_url_shortener.database.models.user import UserModel
from mw_url_shortener.database.start import AsyncSession, sessionmaker
from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate
from mw_url_shortener.security import hash_password, verify_password

from .base import DBInterfaceBase


class UserDBInterface(
    DBInterfaceBase[User, UserCreate, UserUpdate],
):
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
        create_object_schema: UserCreate,
    ) -> User:
        password = create_object_schema.password
        create_data = create_object_schema.dict(exclude={"password"})
        create_data["hashed_password"] = hash_password(password)

        user_model = self.model(**create_data)
        async with async_session.begin():
            async_session.add(user_model)
        await async_session.refresh(user_model)
        await async_session.close()
        return self.schema.from_orm(user_model)

    async def update(
        self,
        async_session: AsyncSession,
        *,
        current_object_schema: User,
        update_object_schema: UserUpdate,
    ) -> User:
        if update_object_schema.password is not None:
            hashed_password = hash_password(update_object_schema.password)
            password_data = {"hashed_password": hashed_password}
            current_object_schema = current_object_schema.copy(update=password_data)
            update_object_schema = update_object_schema.copy(exclude={"password"})

        return await super().update(
            async_session,
            current_object_schema=current_object_schema,
            update_object_schema=update_object_schema,
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

            assert isinstance(
                user_model, UserModel
            ), f"expected '{UserModel}', got '{type(user_model)}'"

            assert (
                user_model.hashed_password
            ), f"user missing hashed password: {user_model}"

            if not verify_password(password, user_model.hashed_password):
                return None
            return self.schema.from_orm(user_model)

    async def search(
        self,
        async_session: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        id: Optional[int] = None,
        username: Optional[str] = None,
    ) -> List[User]:
        query = select(UserModel)

        if id is not None:
            query = query.where(UserModel.id == id)
        if username is not None:
            query = query.where(UserModel.username == username)

        query = query.offset(skip).limit(limit).order_by(UserModel.id)

        user_schemas: List[User] = []
        async with async_session.begin():
            user_models = (await async_session.scalars(query)).all()

            for user_model in user_models:
                user_schema = self.schema.from_orm(user_model)
                user_schemas.append(user_schema)
        return user_schemas


user = UserDBInterface(UserModel, User)
