from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException

from src.application.use_cases.base import UseCase
from src.application.use_cases.user_use_cases import GetUserByEmail
from src.domain.services.auth_service import AuthService
from src.infrastructure.logger.interfaces import ILogger
from src.presentation.routers.schemas import Token


class AuthUser(UseCase[OAuth2PasswordRequestForm, Token]):

    def __init__(self, get_user: UseCase, auth_service: AuthService, logger: ILogger):
        self.get_user: GetUserByEmail = get_user
        self.auth_service = auth_service
        self.logger = logger

    async def __call__(self, form_data: OAuth2PasswordRequestForm) -> Token:
        try:
            user = await self.get_user(form_data.username)
            access_token = self.auth_service.get_access_token(form_data, user)

            return Token(access_token=access_token)
        except HTTPException as ex:
            raise ex
        except Exception:
            self.logger.error(f'Ошибка при авторизации пользователя {form_data.username}')
            raise HTTPException(status_code=500)
