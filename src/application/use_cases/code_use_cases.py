from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.application.use_cases.base import UseCase
from src.domain.entities import User, Code
from src.infrastructure.logger.interfaces import ILogger
from src.infrastructure.models import UserModel, CodeModel
from src.infrastructure.uow.interfaces import IUnitOfWork
from src.presentation.routers.schemas import UserSchema, MeSchema, CodeSchema


class CreateCode(UseCase[[UserSchema, Code], CodeSchema]):

    def __init__(self, uow: IUnitOfWork, logger: ILogger):
        self.uow = uow
        self.logger = logger

    async def __call__(self, user: UserSchema) -> CodeSchema:
        try:
            async with self.uow:
                db_code = CodeModel(value=Code.generate_code(), user_email=user.email)
                try:
                    await self.uow.codes.add(db_code)
                    await self.uow.commit()
                    self.logger.info(f'Создан реферальный код для пользователя: {user.email}')
                except IntegrityError:
                    raise HTTPException(status_code=400, detail='Code already exists')
                return CodeSchema(code=db_code.value)

        except HTTPException as ex:
            raise ex
        except Exception:
            self.logger.error(f'Ошибка при создании реферального кода: {user}')
            raise HTTPException(status_code=500)


class GetCode(UseCase[User, CodeSchema]):

    def __init__(self, uow: IUnitOfWork, logger: ILogger):
        self.uow = uow
        self.logger = logger

    async def __call__(self, email: str) -> CodeSchema:
        try:
            async with self.uow:
                code: CodeModel = await self.uow.codes.find_one(CodeModel.user_email, email)
                code_not_found = HTTPException(status_code=404, detail='Code not found')

                if not code:
                    raise code_not_found

                if code.is_code_expired():
                    await self.uow.codes.delete_one(CodeModel.id, code.id)
                    await self.uow.commit()
                    raise code_not_found

                return CodeSchema(code=code.value)
        except HTTPException as ex:
            raise ex
        except Exception:
            self.logger.error(f'Ошибка при получении кода по Email: {email}')
            raise HTTPException(status_code=500)


class DeleteCode(UseCase[User, None]):

    def __init__(self, uow: IUnitOfWork, logger: ILogger):
        self.uow = uow
        self.logger = logger

    async def __call__(self, user: MeSchema):
        try:
            async with self.uow:
                db_user = await self.uow.users.find_one(UserModel.email, user.email)

                if db_user.code:
                    await self.uow.codes.delete_one(CodeModel.id, db_user.code.id)
                    await self.uow.commit()
                    self.logger.info(f'Удалён код у пользователя: {user.id}')
        except Exception:
            self.logger.error(f'Ошибка при удалении кода у пользователя: {user}')
            raise HTTPException(status_code=500)
