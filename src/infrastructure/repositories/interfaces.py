from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy.orm import InstrumentedAttribute

from src.domain.entities import Code
from src.infrastructure.models import Base, CodeModel, RoleModel, UserModel

T = TypeVar('T', bound=Base)


class ISQLAlchemyRepository(ABC, Generic[T]):

    @abstractmethod
    async def add(self, data: T) -> T:
        raise NotImplementedError

    @abstractmethod
    async def find_all(
            self,
            filter_field: InstrumentedAttribute | None = None,
            filter_value: Any = None,
            order_by: InstrumentedAttribute | None = None
    ) -> list[T]:
        raise NotImplementedError

    @abstractmethod
    async def find_one(
            self,
            filter_field: InstrumentedAttribute | None = None,
            filter_value: Any = None
    ) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def update(
            self, values: dict,
            filter_field: InstrumentedAttribute | None = None,
            filter_value: Any = None
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(
            self,
            filter_field: InstrumentedAttribute,
            filter_value: Any
    ):
        raise NotImplementedError

    @abstractmethod
    async def delete(self):
        raise NotImplementedError


class IUsersRepository(ISQLAlchemyRepository[UserModel], ABC):

    @abstractmethod
    async def find_by_email(self, email: str) -> UserModel | None:
        raise NotImplementedError

    @abstractmethod
    async def find_by_code(self, code: Code) -> UserModel | None:
        raise NotImplementedError


class ICodesRepository(ISQLAlchemyRepository[CodeModel], ABC):
    pass


class IRolesRepository(ISQLAlchemyRepository[RoleModel], ABC):
    pass
