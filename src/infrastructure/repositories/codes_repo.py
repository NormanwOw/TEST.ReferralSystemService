from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import CodeModel
from src.infrastructure.repositories.base import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import ICodesRepository


class CodesRepository(SQLAlchemyRepository, ICodesRepository):

    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, CodeModel)
