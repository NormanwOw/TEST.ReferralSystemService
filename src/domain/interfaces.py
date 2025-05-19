from abc import ABC, abstractmethod
from datetime import timedelta

from src.domain.entities import User


class ITokenService(ABC):

    @abstractmethod
    def create_access_token(self, user: User, expires_delta: timedelta | None = None) -> str:
        raise NotImplementedError

    def decode_token(self, token: str) -> dict:
        raise NotImplementedError


class IPasswordHasher(ABC):

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        raise NotImplementedError

    def hash(self, password: str) -> str:
        raise NotImplementedError