import time
from hashlib import sha256

from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


class TTLCache:

    __ttl_sec: int = 0
    _ttl_mapper = {}

    @property
    def ttl_sec(self) -> int:
        return self.__ttl_sec

    @ttl_sec.setter
    def ttl_sec(self, ttl: int):
        self.validate_ttl(ttl)
        self.__ttl_sec = ttl

    def validate_ttl(self, ttl: int):
        if not isinstance(ttl, int):
            raise TypeError('ttl_sec must be an integer')
        if ttl < 0:
            raise ValueError('ttl_sec cannot be negative')

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if 'ttl_sec' in cls.__dict__:
            ttl_value = cls.__dict__['ttl_sec']
            TTLCache.validate_ttl(cls, ttl_value)
            cls.__ttl_sec = ttl_value
            delattr(cls, 'ttl_sec')


class DeclarativeBaseWithCache(DeclarativeBase, TTLCache):
    __abstract__ = True

    __cache = {}

    def __init__(self, **kwargs):
        all_columns = [c.key for c in inspect(self.__class__).column_attrs if c.key != 'id']
        full_data = {col: kwargs.get(col) for col in all_columns}
        for_hash = ';'.join(f'{k}={v}'for k, v in sorted(full_data.items(), key=lambda item: item[0]))
        str_hash = sha256(f'{self.__class__.__name__} {for_hash}'.encode()).hexdigest()
        instance = self.from_cache(str_hash)
        attrs = instance.to_dict() if instance else kwargs
        for k, v in attrs.items():
            setattr(self, k, v)

    def __hash__(self):
        data = self.to_dict()
        data.pop('id', None)
        for_hash = ';'.join(f'{k}={v}' for k, v in sorted(data.items(), key=lambda item: item[0]))
        return sha256(f'{self.__class__.__name__} {for_hash}'.encode()).hexdigest()

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    def to_cache(self, str_hash: str, ttl_sec: int = 0):
        self.__cache[str_hash] = self
        ttl = ttl_sec or self.ttl_sec
        if ttl:
            self.validate_ttl(ttl_sec)
            self._ttl_mapper[str_hash] = time.time() + ttl

    def from_cache(self, str_hash: str = None):
        if not str_hash:
            str_hash = self.__hash__()
        ttl = self._ttl_mapper.get(str_hash)
        if ttl and time.time() > ttl:
            self._ttl_mapper.pop(str_hash)
            return
        return self.__cache.get(str_hash)
