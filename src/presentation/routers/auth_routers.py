from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from config import VERSION
from src.application.use_cases.auth_use_cases import AuthUser
from src.application.use_cases.user_use_cases import RegisterUser
from src.presentation.routers.dependencies import AuthDependencies
from src.presentation.routers.forms import RegistrationForm
from src.presentation.routers.schemas import Token, MeSchema

router = APIRouter(
    prefix=f'/api/v{VERSION}/auth',
    tags=['Auth']
)


@router.post('/token')
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_user: Annotated[AuthUser, Depends(AuthDependencies.auth_user)],
) -> Token:
    return await auth_user(form_data)


@router.post('/registration', status_code=201, summary='Регистрация')
async def register_user(
        form_data: Annotated[RegistrationForm, Depends()],
        register_user: RegisterUser = Depends(AuthDependencies.register_user)
):
    await register_user(form_data)
    return Response(status_code=201)


@router.get('/me', summary='Мои данные')
async def read_users_me(
    current_user: Annotated[MeSchema, Depends(AuthDependencies.get_active_user)],
) -> MeSchema:
    return current_user
