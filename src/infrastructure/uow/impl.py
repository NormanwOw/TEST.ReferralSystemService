from src.infrastructure.repositories.codes_repo import CodesRepository
from src.infrastructure.repositories.users_repo import UsersRepository
from src.infrastructure.uow.interfaces import IUnitOfWork


class UnitOfWork(IUnitOfWork):

    def __init__(self, session_factory):
        self.__session_factory = session_factory

    async def __aenter__(self):
        self.__session = self.__session_factory()
        self.users: UsersRepository = UsersRepository(self.__session)
        self.codes: CodesRepository = CodesRepository(self.__session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            await self.rollback()
        await self.__session.close()

    async def commit(self):
        await self.__session.commit()

    async def rollback(self):
        await self.__session.rollback()
