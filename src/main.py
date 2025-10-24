from contextlib import asynccontextmanager
from typing import AsyncIterator

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from config import VERSION
from src.infrastructure.logger.logger import Logger
from src.infrastructure.models import UserModel
from src.infrastructure.session import async_session
from src.infrastructure.uow.impl import UnitOfWork
from src.presentation.containers import UserProvider, CodeProvider, AuthProvider
from src.presentation.routers.auth_routers import router as auth_router
from src.presentation.routers.user_routers import router as user_router


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
    uow = UnitOfWork(async_session)
    async with uow:
        user = UserModel(
            email='<EMAIL>',
            password='<PASSWORD>',
            disabled=False,
        )
        user = await uow.users.add(user, cache=True)
        cached_user = UserModel(
            email='<EMAIL>',
            password='<PASSWORD>',
            disabled=False
        )
        assert user.id == cached_user.id

    logger = Logger()
    logger.info('Start app...')
    yield
    logger.info('App shutdown')

app = FastAPI(
    title='Referral System Service',
    version='1.0.0',
    docs_url=f'/api/v{VERSION}/docs',
    openapi_url=f'/api/v{VERSION}/openapi.json',
    redoc_url=None,
    lifespan=lifespan
)

container = make_async_container(UserProvider(), CodeProvider(), AuthProvider())
setup_dishka(container, app)

app.include_router(
    auth_router
)
app.include_router(
    user_router
)
