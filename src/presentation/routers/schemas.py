from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = 'Bearer'


class UserResponse(BaseModel):
    email: Optional[EmailStr] = None


class UserSchema(UserResponse):
    code: Optional[str] = None


class MeSchema(UserSchema):
    id: UUID


class CodeSchema(BaseModel):
    code: str
