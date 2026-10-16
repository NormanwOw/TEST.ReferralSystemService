from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.models import RoleModel
from src.infrastructure.repositories.base import SQLAlchemyRepository
from src.infrastructure.repositories.interfaces import IRolesRepository


class RolesRepository(SQLAlchemyRepository, IRolesRepository):

    def __init__(self, session: AsyncSession):
        self.__session = session
        super().__init__(session, RoleModel)
