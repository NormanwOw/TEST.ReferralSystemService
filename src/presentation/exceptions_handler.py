from functools import wraps
from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR
)

from src.domain.exceptions import (
    AlreadyExistUserException,
    UserNotFoundException,
    CodeNotFoundException,
    UnauthorizedException,
    InactiveUserException,
    InternalServerException, CodeExpiredException, InvalidPasswordException
)


def handle_domain_exceptions(func):

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AlreadyExistUserException:
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail='User already exists')
        except UserNotFoundException:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
        except CodeNotFoundException:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Code not found')
        except CodeExpiredException:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Code expired')
        except UnauthorizedException:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Unauthorized')
        except InactiveUserException:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Inactive user')
        except InternalServerException:
            raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error')
        except InvalidPasswordException:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Invalid password')

    return wrapper