from abc import ABC, abstractmethod

from src.infrastructure.repositories.interfaces import ICodesRepository, IRolesRepository, IUsersRepository


class IUnitOfWork(ABC):

    @property
    @abstractmethod
    def codes(self) -> ICodesRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def roles(self) -> IRolesRepository:
        raise NotImplementedError

    @property
    @abstractmethod
    def users(self) -> IUsersRepository:
        raise NotImplementedError

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
