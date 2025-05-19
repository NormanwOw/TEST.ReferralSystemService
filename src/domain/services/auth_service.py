from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm

from config import Settings
from src.application.use_cases.base import UseCase
from src.domain.entities import User
from src.domain.exceptions import (
    UnauthorizedException, InactiveUserException, InvalidPasswordException, AppException
)
from src.domain.interfaces import ITokenService, IPasswordHasher
from src.infrastructure.logger.interfaces import ILogger
from src.presentation.routers.schemas import MeSchema


class AuthService:

    def __init__(
        self,
        token_service: ITokenService,
        hasher: IPasswordHasher,
        settings: Settings,
        get_user: UseCase,
        logger: ILogger
    ):
        self.token_service = token_service
        self.hasher = hasher
        self.settings = settings
        self.get_user = get_user
        self.logger = logger

    async def get_current_user(self, token: str) -> User:

        payload = self.token_service.decode_token(token)
        email: str = payload.get('sub')
        if email is None:
            raise UnauthorizedException()

        return await self.get_user(email)

    async def get_current_active_user(self, token: str) -> MeSchema:
        try:
            user = await self.get_current_user(token)
            if user.disabled:
                raise InactiveUserException()
            return MeSchema(id=user.id, email=user.email, code=user.code)
        except AppException as ex:
            raise ex
        except Exception as ex:
            self.logger.error("Ошибка при получении активного пользователя")
            raise ex

    def authenticate_user(self, password: str, user: User):
        if not self.hasher.verify(password, user.hashed_password):
            raise InvalidPasswordException()

    def get_access_token(self, form_data: OAuth2PasswordRequestForm, user: User, ttl: timedelta) -> str:
        try:
            self.authenticate_user(form_data.password, user)
            return self.token_service.create_access_token(user, expires_delta=ttl)
        except AppException as ex:
            raise ex
        except Exception as ex:
            self.logger.error(f"Ошибка при создании токена для пользователя {user.id}")
            raise ex
