import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from hashlib import sha256

import pytz
from sqlalchemy import UUID, Column, ForeignKey, inspect
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

from config import settings


class SQLAlchemyCache(DeclarativeBase):
    __abstract__ = True

    _cache = {}

    def __init__(self, **kwargs):
        data = ';'.join(f'{k}={v}'for k, v in kwargs.items())
        hash = sha256(f'{self.__class__.__name__} {data}'.encode()).hexdigest()
        instance = self._cache.get(hash)
        attrs = instance.to_dict() if instance else kwargs
        for k, v in attrs.items():
            setattr(self, k, v)

    def __hash__(self):
        data = ';'.join(f'{k}={v}' for k, v in self.__dict__.items() if k != '_sa_instance_state')
        return sha256(f'{self.__class__.__name__} {data}'.encode()).hexdigest()

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def to_cache(self, hash: str):
        self._cache[hash] = self

    def from_cache(self):
        return self._cache.get(self.__hash__())


class Base(SQLAlchemyCache):
    __abstract__ = True

    id: Mapped[uuid] = mapped_column(
        UUID, nullable=False, primary_key=True, unique=True, default=uuid.uuid4
    )


class CodeModel(Base):
    __tablename__ = 'codes'

    value: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    user_email: Mapped[str] = mapped_column(
        ForeignKey('users.email', ondelete='CASCADE'), nullable=False, unique=True
    )
    user = relationship(
        'UserModel',
        back_populates='code',
        uselist=False,
        lazy='selectin'
    )

    def is_code_expired(self) -> bool:
        tz = pytz.timezone('Europe/Moscow')
        return (
          self.created_at + timedelta(days=settings.REFERRAL_CODE_EXPIRE_DAYS)
        ).replace(tzinfo=tz) < datetime.now(tz=tz)


class UserModel(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(nullable=False)
    disabled: Mapped[bool] = mapped_column()
    referrer_id: Mapped[Optional[int]] = mapped_column(ForeignKey('users.id'), nullable=True)

    code: Mapped[CodeModel] = relationship(
        CodeModel,
        back_populates='user',
        uselist=False,
        primaryjoin='UserModel.email == CodeModel.user_email',
        lazy='selectin'
    )
    referrer: Mapped['UserModel'] = relationship(
        'UserModel',
        remote_side='UserModel.id',
        back_populates='referrals',
        uselist=False,
        lazy='joined'
    )
    referrals: Mapped[List['UserModel']] = relationship(
        'UserModel',
        back_populates='referrer',
        cascade='all, delete-orphan',
        uselist=True,
        lazy='joined'
    )
