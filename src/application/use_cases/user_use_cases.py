from typing import List
from uuid import UUID

from src.application.use_cases.base import UseCase
from src.domain.entities import User, Code
from src.domain.exceptions import AppException, AlreadyExistUserException, UserNotFoundException, \
    CodeNotFoundException, CodeExpiredException
from src.domain.interfaces import IPasswordHasher
from src.domain.services.auth_service import AuthService
from src.infrastructure.logger.interfaces import ILogger
from src.infrastructure.models import UserModel, CodeModel
from src.infrastructure.uow.interfaces import IUnitOfWork
from src.presentation.routers.forms import RegistrationForm
from src.presentation.routers.schemas import UserResponse


class GetUserByEmail(UseCase[str, User]):

    def __init__(self, uow: IUnitOfWork, logger: ILogger):
        self.uow = uow
        self.logger = logger

    async def __call__(self, email: str) -> User:
        try:
            async with self.uow:
                user = await self.uow.users.find_by_email(email)
                if not user:
                    raise UserNotFoundException()

                return User(
                    id=user.id,
                    email=user.email,
                    disabled=user.disabled,
                    code=user.code.value if user.code else None,
                    hashed_password=user.password
                )
        except AppException as ex:
            raise ex
        except Exception as ex:
            self.logger.error(f'Ошибка при получении пользователя по Email: {email}')
            raise ex


class GetReferralsByUserID(UseCase[UUID, List[UserResponse]]):

    def __init__(self, uow: IUnitOfWork, logger: ILogger):
        self.uow = uow
        self.logger = logger

    async def __call__(self, user_id: UUID) -> List[UserResponse]:
        try:
            async with self.uow:
                user = await self.uow.users.find_one(UserModel.id, user_id)
                if not user:
                    raise UserNotFoundException()

                return [
                    UserResponse(email=referral.email) for referral in user.referrals
                ]
        except AppException as ex:
            raise ex
        except Exception:
            self.logger.error(f'Ошибка при получении рефералов по ID пользователя: {user_id}')


class RegisterUser(UseCase[Code, None]):

    def __init__(
        self,
        uow: IUnitOfWork,
        auth_service: AuthService,
        hasher: IPasswordHasher,
        logger: ILogger
    ):
        self.uow = uow
        self.auth_service = auth_service
        self.hasher = hasher
        self.logger = logger

    async def __call__(self, form_data: RegistrationForm):
        try:
            async with self.uow:
                user = await self.uow.users.find_by_email(form_data.email)

                if user:
                    raise AlreadyExistUserException()

                user = await self.uow.users.find_by_code(Code(value=form_data.code))
                if not user:
                    raise CodeNotFoundException()

                if user.code.is_code_expired():
                    await self.uow.codes.delete_one(CodeModel.id, user.code.id)
                    await self.uow.commit()
                    raise CodeExpiredException()

                hashed_password = self.hasher.hash(form_data.password)
                new_user = UserModel(
                    email=form_data.email,
                    password=hashed_password,
                    disabled=False,
                    referrer_id=user.id
                )
                await self.uow.users.add(new_user)
                await self.uow.commit()
                self.logger.info(f'Зарегистрирован пользователь {new_user.email}')
        except AppException as ex:
            raise ex
        except Exception as ex:
            self.logger.error(f'Ошибка при регистрации пользователя:\n'
                              f'Email: {form_data.email}\n'
                              f'Password: {form_data.password}\n'
                              f'Code: {form_data.code}\n')
            raise ex
