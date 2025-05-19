from passlib.context import CryptContext

from src.domain.interfaces import IPasswordHasher


class BcryptHasher(IPasswordHasher):

    def __init__(self):
        self.context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.context.verify(plain_password, hashed_password)

    def hash(self, password: str) -> str:
        return self.context.hash(password)