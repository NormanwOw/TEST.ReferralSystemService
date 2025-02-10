from typing import Annotated

from fastapi import Form
from pydantic import EmailStr


class RegistrationForm:

    def __init__(
            self,
            email: Annotated[EmailStr, Form()],
            password: Annotated[str, Form(min_length=6)],
            code: Annotated[str, Form()]
    ):
        self.email = email
        self.password = password
        self.code = code
