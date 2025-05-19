from asyncpg.pgproto.pgproto import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from config import Settings
from src.application.use_cases.base import UseCase
from src.application.use_cases.user_use_cases import GetUserByEmail
from src.domain.exceptions import AppException
from src.domain.services.auth_service import AuthService
from src.infrastructure.logger.interfaces import ILogger
from src.presentation.routers.schemas import Token


class AuthUser(UseCase[OAuth2PasswordRequestForm, Token]):

    def __init__(
        self,
        get_user: UseCase,
        auth_service: AuthService,
        settings: Settings,
        logger: ILogger
    ):
        self.get_user: GetUserByEmail = get_user
        self.auth_service = auth_service
        self.settings = settings
        self.logger = logger

    async def __call__(self, form_data: OAuth2PasswordRequestForm) -> Token:
        try:
            user = await self.get_user(form_data.username)
            ttl = timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.auth_service.get_access_token(form_data, user, ttl)
            return Token(access_token=access_token)
        except AppException as ex:
            raise ex
        except Exception as ex:
            self.logger.error(f'Ошибка при авторизации пользователя {form_data.username}')
            raise ex

