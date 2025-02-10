from abc import ABC, abstractmethod


class ILogger(ABC):

    @abstractmethod
    def info(self, message: str):
        raise NotImplementedError

    @abstractmethod
    def error(self, message: str):
        raise NotImplementedError

    @abstractmethod
    def warning(self, message: str):
        raise NotImplementedError

    @abstractmethod
    def debug(self, message: str):
        raise NotImplementedError
