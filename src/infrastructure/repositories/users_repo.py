from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import joinedload, InstrumentedAttribute
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import Code
from src.infrastructure.models import UserModel, CodeModel
from src.infrastructure.repositories.base import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import IUsersRepository


class UsersRepository(SQLAlchemyRepository, IUsersRepository):

    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, UserModel)

    async def find_by_email(self, email: str) -> UserModel:
        user = await self.__session.scalars(
            select(UserModel).where(email == UserModel.email).options(
                joinedload(UserModel.referrer),
                joinedload(UserModel.referrals),
            )
        )
        return user.first()

    async def find_by_code(self, code: Code) -> UserModel:
        user = await self.__session.scalars(
            select(UserModel).join(CodeModel).where(code.value == CodeModel.value).options(
                joinedload(UserModel.referrer),
                joinedload(UserModel.referrals),
            )
        )
        return user.first()

    async def find_one(
            self, filter_field: InstrumentedAttribute = None, filter_value: Any = None
    ) -> UserModel:
        user = await self.__session.scalars(
            select(UserModel).where(filter_field == filter_value).options(
                joinedload(UserModel.referrer),
                joinedload(UserModel.referrals),
            )
        )
        return user.first()
