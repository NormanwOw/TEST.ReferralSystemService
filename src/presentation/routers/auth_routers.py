from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from config import VERSION, oauth2_scheme
from src.application.use_cases.auth_use_cases import AuthUser
from src.application.use_cases.user_use_cases import RegisterUser
from src.domain.services.auth_service import AuthService
from src.presentation.exceptions_handler import handle_domain_exceptions
from src.presentation.routers.forms import RegistrationForm
from src.presentation.routers.schemas import Token, MeSchema

router = APIRouter(
    prefix=f'/api/v{VERSION}/auth',
    tags=['Auth']
)


@router.post('/token')
@handle_domain_exceptions
@inject
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_user: FromDishka[AuthUser],
) -> Token:
    return await auth_user(form_data)


@router.post('/registration', status_code=201, summary='Регистрация')
@handle_domain_exceptions
@inject
async def register_user(
    form_data: Annotated[RegistrationForm, Depends()],
    register_user: FromDishka[RegisterUser],
):
    await register_user(form_data)
    return Response(status_code=201)


@router.get('/me', summary='Мои данные')
@handle_domain_exceptions
@inject
async def read_users_me(
    auth_service: FromDishka[AuthService],
    token: str = Depends(oauth2_scheme)
) -> MeSchema:
    return await auth_service.get_current_active_user(token)
