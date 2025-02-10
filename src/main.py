from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from config import VERSION, REDIS_URL
from src.infrastructure.logger.logger import Logger
from src.presentation.routers.auth_routers import router as auth_router
from src.presentation.routers.user_routers import router as user_router


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncIterator[None]:
    logger = Logger()
    redis = aioredis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
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

app.include_router(
    auth_router
)
app.include_router(
    user_router
)
