# mypy: allow_any_expr
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import select

from mw_url_shortener.database.models.user import UserModel
from mw_url_shortener.database.start import AsyncSession, sessionmaker
from mw_url_shortener.schemas.user import User, UserCreate, UserUpdate
from mw_url_shortener.security import hash_password, verify_password

from ..user_interface import UserInterface
from .base import DBInterfaceBase


class UserDBInterface(
    DBInterfaceBase[User, UserCreate, UserUpdate], UserInterface[AsyncSession]
):
    async def get_by_username(
        self, opened_resource: AsyncSession, /, *, username: str
    ) -> Optional[User]:
        async with opened_resource.begin():
            user_model = (
                await opened_resource.execute(
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
        opened_resource: AsyncSession,
        /,
        *,
        create_object_schema: UserCreate,
    ) -> Optional[User]:
        get_username = select(self.model).where(
            UserModel.username == create_object_schema.username
        )
        async with opened_resource.begin():
            non_existent_user_model = (
                await opened_resource.execute(get_username)
            ).scalar_one_or_none()
            if non_existent_user_model is not None:
                return None

        password = create_object_schema.password
        create_data = create_object_schema.dict(exclude={"password"})
        create_data["hashed_password"] = hash_password(password)

        user_model = self.model(**create_data)

        async with opened_resource.begin():
            opened_resource.add(user_model)
        await opened_resource.refresh(user_model)
        await opened_resource.close()
        return self.schema.from_orm(user_model)

    async def update(
        self,
        opened_resource: AsyncSession,
        /,
        *,
        current_object_schema: User,
        update_object_schema: UserUpdate,
    ) -> Optional[User]:
        if update_object_schema.password is not None:
            hashed_password = hash_password(update_object_schema.password)
            password_data = {"hashed_password": hashed_password}
            current_object_schema = current_object_schema.copy(update=password_data)
            update_object_schema = update_object_schema.copy(exclude={"password"})

        return await super().update(
            opened_resource,
            current_object_schema=current_object_schema,
            update_object_schema=update_object_schema,
        )

    async def authenticate(
        self, opened_resource: AsyncSession, /, *, username: str, password: str
    ) -> Optional[User]:
        async with opened_resource.begin():
            user_model = (
                await opened_resource.execute(
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
        opened_resource: AsyncSession,
        /,
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
        async with opened_resource.begin():
            user_models = (await opened_resource.scalars(query)).all()

            for user_model in user_models:
                user_schema = self.schema.from_orm(user_model)
                user_schemas.append(user_schema)
        return user_schemas


user = UserDBInterface(UserModel, User)
