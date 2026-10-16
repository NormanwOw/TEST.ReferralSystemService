from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload, InstrumentedAttribute
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Code
from src.infrastructure.models import UserModel, CodeModel
from src.infrastructure.repositories.base import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import IUsersRepository


class UsersRepository(SQLAlchemyRepository[UserModel], IUsersRepository):

    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, UserModel)

    async def find_by_email(self, email: str) -> UserModel | None:
        user = await self.__session.scalars(
            select(UserModel).where(UserModel.email == email).options(
                joinedload(UserModel.referrer),
                joinedload(UserModel.referrals),
            )
        )
        return user.first()

    async def find_by_code(self, code: Code) -> UserModel | None:
        user = await self.__session.scalars(
            select(UserModel).join(CodeModel).where(CodeModel.value == code.value).options(
                joinedload(UserModel.referrer),
                joinedload(UserModel.referrals),
            )
        )
        return user.first()

    async def find_one(
            self,
            filter_field: InstrumentedAttribute | None = None,
            filter_value: Any = None
    ) -> UserModel | None:
        query = select(UserModel)
        if filter_field is not None and filter_value is not None:
            query = query.where(filter_field == filter_value)
        user = await self.__session.scalars(
            query.options(
                joinedload(UserModel.referrer),
                joinedload(UserModel.referrals),
            )
        )
        return user.first()
