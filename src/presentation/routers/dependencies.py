from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from config import settings
from src.application.use_cases.auth_use_cases import AuthUser
from src.application.use_cases.code_use_cases import CreateCode, DeleteCode, GetCode
from src.application.use_cases.user_use_cases import GetUserByEmail, RegisterUser, GetReferralsByUserID
from src.domain.services.auth_service import AuthService
from src.infrastructure.logger.logger import Logger
from src.infrastructure.session import async_session
from src.infrastructure.uow.impl import UnitOfWork
from src.presentation.routers.schemas import MeSchema


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


class AuthDependencies:

    uow = UnitOfWork(async_session)
    logger = Logger()
    get_user = GetUserByEmail(uow, logger)
    auth_service = AuthService(settings, get_user, logger)

    @classmethod
    async def get_active_user(cls, token: Annotated[str, Depends(oauth2_scheme)]) -> MeSchema:
        return await cls.auth_service.get_current_active_user(token)

    @classmethod
    async def auth_user(cls) -> AuthUser:
        return AuthUser(cls.get_user, cls.auth_service, cls.logger)

    @classmethod
    async def register_user(cls) -> RegisterUser:
        return RegisterUser(cls.uow, cls.auth_service, cls.logger)


class UserDependencies:

    uow = UnitOfWork(async_session)
    logger = Logger()

    @classmethod
    async def get_code(cls):
        return GetCode(cls.uow, cls.logger)

    @classmethod
    async def create_code(cls):
        return CreateCode(cls.uow, cls.logger)

    @classmethod
    async def delete_code(cls):
        return DeleteCode(cls.uow, cls.logger)

    @classmethod
    async def get_referrals(cls):
        return GetReferralsByUserID(cls.uow, cls.logger)
