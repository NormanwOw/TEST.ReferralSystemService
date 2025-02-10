import logging
from functools import wraps
from logging.handlers import RotatingFileHandler

from fastapi import HTTPException

from src.infrastructure.logger.interfaces import ILogger


class Logger(ILogger):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.__logger = logging.getLogger()
        self.__logger.setLevel(level=logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        file_handler = RotatingFileHandler(
            filename='logs/logs.log',
            mode='w',
            maxBytes=1048576,
            backupCount=2
        )
        file_handler.setFormatter(formatter)
        self.__logger.addHandler(file_handler)

    def info(self, message):
        self.__logger.info(message)

    def error(self, message):
        self.__logger.error(message, exc_info=True)

    def warning(self, message):
        self.__logger.warning(message)

    def debug(self, message):
        self.__logger.debug(message)


logger = Logger()


def error_decorator(message):
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result
            except HTTPException as ex:
                raise ex
            except Exception:
                logger.error(message)
        return inner
    return wrapper
