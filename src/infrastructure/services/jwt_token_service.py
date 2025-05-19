from datetime import datetime, timezone, timedelta

import jwt

from src.domain.entities import User
from src.domain.interfaces import ITokenService


class JWTTokenService(ITokenService):

    def __init__(self, secret_key: str, algorithm: str):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_access_token(self, user: User, expires_delta: timedelta | None = None) -> str:
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        return jwt.encode(
            payload={'sub': user.email, 'exp': expire},
            key=self.secret_key,
            algorithm=self.algorithm
        )

    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])