from datetime import timedelta, datetime, timezone

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jwt import InvalidTokenError
from passlib.context import CryptContext
import jwt

from config import Settings, settings
from src.application.use_cases.base import UseCase
from src.domain.entities import User
from src.infrastructure.logger.interfaces import ILogger
from src.presentation.routers.schemas import MeSchema


class AuthService:

    def __init__(self, settings: Settings, get_user: UseCase, logger: ILogger):
        self.settings = settings
        self.get_user = get_user
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.logger = logger

    async def get_current_user(self, token: str) -> User:
        credentials_exception = HTTPException(
            status_code=401,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get('sub')
            if email is None:
                raise credentials_exception

        except InvalidTokenError:
            raise credentials_exception

        return await self.get_user(email)

    async def get_current_active_user(self, token: str) -> MeSchema:
        try:
            current_user = await self.get_current_user(token)
            if current_user.disabled:
                raise HTTPException(status_code=400, detail='Inactive user')
            return MeSchema(
                id=current_user.id,
                email=current_user.email,
                code=current_user.code,
            )
        except HTTPException as ex:
            raise ex
        except Exception:
            self.logger.error('Ошибка при получении информации о пользователе')
            raise HTTPException(status_code=500)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def authenticate_user(self, password: str, user: User):
        if not self.verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail='Incorrect username or password',
                headers={'WWW-Authenticate': 'Bearer'},
            )

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, self.settings.SECRET_KEY, algorithm=self.settings.ALGORITHM)
        return encoded_jwt

    def get_access_token(self, form_data: OAuth2PasswordRequestForm, user: User) -> str:
        try:
            self.authenticate_user(form_data.password, user)
            token = self.create_access_token(
                data={'sub': user.email},
                expires_delta=timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            self.logger.info(f'Создан токен для пользователя {user.id}')
            return token

        except HTTPException as ex:
            raise ex
        except Exception:
            self.logger.error(f'Ошибка при создании access_token у пользователя {user.id}')
            raise HTTPException(status_code=500)
