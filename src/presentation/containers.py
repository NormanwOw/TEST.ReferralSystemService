from dishka import Provider, Scope, provide, FromDishka
from fastapi import Depends

from config import settings, oauth2_scheme
from src.application.use_cases.auth_use_cases import AuthUser
from src.application.use_cases.code_use_cases import CreateCode, DeleteCode, GetCode
from src.application.use_cases.user_use_cases import GetUserByEmail, GetReferralsByUserID, RegisterUser
from src.domain.interfaces import IPasswordHasher, ITokenService
from src.domain.services.auth_service import AuthService
from src.infrastructure.logger.logger import logger
from src.infrastructure.password_hasher import BcryptHasher
from src.infrastructure.services.jwt_token_service import JWTTokenService
from src.infrastructure.session import async_session
from src.infrastructure.uow.impl import UnitOfWork
from src.infrastructure.uow.interfaces import IUnitOfWork
from src.presentation.routers.schemas import MeSchema


class UserProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def get_uow(self) -> IUnitOfWork:
        return UnitOfWork(session_factory=async_session)

    @provide(scope=Scope.REQUEST)
    def get_user_by_email(self, uow: IUnitOfWork) -> GetUserByEmail:
        return GetUserByEmail(uow, logger)

    @provide(scope=Scope.REQUEST)
    def get_referrals_by_user_id(self, uow: IUnitOfWork) -> GetReferralsByUserID:
        return GetReferralsByUserID(uow, logger)


class CodeProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def get_uow(self) -> IUnitOfWork:
        return UnitOfWork(session_factory=async_session)

    @provide(scope=Scope.REQUEST)
    def get_get_code(self, uow: IUnitOfWork) -> GetCode:
        return GetCode(uow, logger)

    @provide(scope=Scope.REQUEST)
    def get_create_code(self, uow: IUnitOfWork) -> CreateCode:
        return CreateCode(uow, logger)

    @provide(scope=Scope.REQUEST)
    def get_delete_code(self, uow: IUnitOfWork) -> DeleteCode:
        return DeleteCode(uow, logger)


class AuthProvider(Provider):

    @provide(scope=Scope.REQUEST)
    def get_uow(self) -> IUnitOfWork:
        return UnitOfWork(session_factory=async_session)

    @provide(scope=Scope.REQUEST)
    def get_hasher(self) -> IPasswordHasher:
        return BcryptHasher()

    @provide(scope=Scope.REQUEST)
    def get_token_service(self) -> ITokenService:
        return JWTTokenService(settings.SECRET_KEY, settings.ALGORITHM)

    @provide(scope=Scope.REQUEST)
    def get_get_user_by_email(self, uow: IUnitOfWork) -> GetUserByEmail:
        return GetUserByEmail(uow, logger)

    @provide(scope=Scope.REQUEST)
    def get_auth_service(
        self,
        token_service: ITokenService,
        hasher: IPasswordHasher,
        get_user: GetUserByEmail
    ) -> AuthService:
        return AuthService(token_service, hasher, settings, get_user, logger)

    @provide(scope=Scope.REQUEST)
    def get_auth_user(self, get_user: GetUserByEmail, auth_service: AuthService) -> AuthUser:
        return AuthUser(get_user, auth_service, settings, logger)

    @provide(scope=Scope.REQUEST)
    def get_register_user(
        self,
        uow: IUnitOfWork,
        auth_service: AuthService,
        hasher: IPasswordHasher
    ) -> RegisterUser:
        return RegisterUser(uow, auth_service, hasher, logger)


async def get_current_user(
    auth_service: FromDishka[AuthService],
    token: str = Depends(oauth2_scheme)
) -> MeSchema:
    return await auth_service.get_current_active_user(token)