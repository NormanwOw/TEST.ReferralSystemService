from typing import List
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Response
from fastapi.params import Depends
from fastapi_cache.decorator import cache
from pydantic import EmailStr

from config import VERSION, oauth2_scheme
from src.application.use_cases.code_use_cases import GetCode, CreateCode, DeleteCode
from src.application.use_cases.user_use_cases import GetReferralsByUserID
from src.domain.services.auth_service import AuthService
from src.presentation.exceptions_handler import handle_domain_exceptions
from src.presentation.routers.schemas import CodeSchema, UserResponse

router = APIRouter(
    prefix=f'/api/v{VERSION}/users',
    tags=['User']
)


@router.post(
    '/codes',
    status_code=201,
    summary='Создание реферального кода',
    description='У каждого пользователя может быть только один код'
)
@handle_domain_exceptions
@inject
async def create_code(
    auth_service: FromDishka[AuthService],
    create_code: FromDishka[CreateCode],
    token: str = Depends(oauth2_scheme)
) -> CodeSchema:
    current_user = await auth_service.get_current_active_user(token)
    return await create_code(current_user)


@router.delete('/codes', status_code=204, summary='Удаление реферального кода')
@handle_domain_exceptions
@inject
async def delete_code(
    auth_service: FromDishka[AuthService],
    delete_code: FromDishka[DeleteCode],
    token: str = Depends(oauth2_scheme)
):
    current_user = await auth_service.get_current_active_user(token)
    await delete_code(current_user)
    return Response(status_code=204)


@router.get('/codes', summary='Получение реферального кода по Email')
@handle_domain_exceptions
@inject
async def get_code(email: EmailStr, get_code: FromDishka[GetCode]) -> CodeSchema:
    return await get_code(email)


@router.get('/{user_id}/referrals', summary='Получение данных о рефералах по ID реферера')
@cache(expire=60)
@handle_domain_exceptions
@inject
async def get_referrals(
    user_id: UUID,
    get_referrals: FromDishka[GetReferralsByUserID],
) -> List[UserResponse]:
    return await get_referrals(user_id)
