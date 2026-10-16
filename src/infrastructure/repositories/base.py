from typing import Any, Generic, TypeVar, Type

from sqlalchemy import select, desc, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from src.infrastructure.models import Base
from src.infrastructure.repositories.interfaces import ISQLAlchemyRepository

T = TypeVar('T', bound=Base)


class SQLAlchemyRepository(ISQLAlchemyRepository[T], Generic[T]):

    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def add(self, data: T) -> T:
        self.session.add(data)
        await self.session.flush()
        return data

    async def find_all(
            self,
            filter_field: InstrumentedAttribute | None = None,
            filter_value: Any = None,
            order_by: InstrumentedAttribute | None = None
    ) -> list[T]:

        if not filter_field or not filter_value:
            if order_by:
                res = await self.session.execute(
                    select(self.model).order_by(desc(order_by))
                )
            else:
                res = await self.session.execute(
                    select(self.model)
                )
            return list(res.scalars().all())

        if order_by:
            query = select(self.model).where(filter_field == filter_value).order_by(desc(order_by))
        else:
            query = select(self.model).where(filter_field == filter_value)
        res = await self.session.execute(query)
        return list(res.scalars().all())

    async def find_one(
            self,
            filter_field: InstrumentedAttribute | None = None,
            filter_value: Any = None
    ) -> T | None:
        if filter_field and filter_value:
            query = select(self.model).where(filter_field == filter_value)
        else:
            query = select(self.model)
        res = await self.session.execute(query)
        return res.scalars().first()

    async def update(
            self, values: dict,
            filter_field: InstrumentedAttribute | None = None,
            filter_value: Any = None
    ):
        if filter_field and filter_value:
            stmt = update(self.model).values(**values).where(filter_field == filter_value)
        else:
            stmt = update(self.model).values(**values)
        await self.session.execute(stmt)

    async def delete_one(
            self,
            filter_field: InstrumentedAttribute,
            filter_value: Any
    ):
        await self.session.execute(
            delete(self.model).where(filter_field == filter_value)
        )

    async def delete(self):
        await self.session.execute(
            delete(self.model)
        )
