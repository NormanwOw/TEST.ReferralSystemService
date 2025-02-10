import random
import string
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Code(BaseModel):
    id: Optional[UUID] = None
    value: Optional[str] = None

    @staticmethod
    def generate_code() -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=24))


class User(BaseModel):
    id: UUID
    email: str
    disabled: bool = False
    code: Optional[str] = None
    hashed_password: str
