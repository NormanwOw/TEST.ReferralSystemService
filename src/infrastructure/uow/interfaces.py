from abc import ABC, abstractmethod

from src.infrastructure.repositories.interfaces import ICodesRepository, IUsersRepository


class IUnitOfWork(ABC):
    codes: ICodesRepository
    users: IUsersRepository

    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError
