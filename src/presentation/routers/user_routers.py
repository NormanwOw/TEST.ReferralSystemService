from typing import List, Annotated
from uuid import UUID

from fastapi import APIRouter, Response
from fastapi.params import Depends
from fastapi_cache.decorator import cache
from pydantic import EmailStr

from config import VERSION
from src.application.use_cases.code_use_cases import GetCode, CreateCode, DeleteCode
from src.application.use_cases.user_use_cases import GetReferralsByUserID
from src.presentation.routers.dependencies import AuthDependencies, UserDependencies
from src.presentation.routers.schemas import CodeSchema, MeSchema, UserResponse

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
async def create_code(
        current_user: Annotated[MeSchema, Depends(AuthDependencies.get_active_user)],
        create_code: CreateCode = Depends(UserDependencies.create_code)
) -> CodeSchema:
    return await create_code(current_user)


@router.delete('/codes', status_code=204, summary='Удаление реферального кода')
async def delete_code(
        current_user: Annotated[MeSchema, Depends(AuthDependencies.get_active_user)],
        delete_code: DeleteCode = Depends(UserDependencies.delete_code)
):
    await delete_code(current_user)
    return Response(status_code=204)


@router.get('/codes', summary='Получение реферального кода по Email')
async def get_code(email: EmailStr, get_code: GetCode = Depends(UserDependencies.get_code)) -> CodeSchema:
    return await get_code(email)


@router.get('/{user_id}/referrals', summary='Получение данных о рефералах по ID реферера')
@cache(expire=60)
async def get_referrals(
        user_id: UUID,
        get_referrals: GetReferralsByUserID = Depends(UserDependencies.get_referrals)
) -> List[UserResponse]:
    return await get_referrals(user_id)
