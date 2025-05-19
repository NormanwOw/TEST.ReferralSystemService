class AppException(Exception):
    pass


class AlreadyExistUserException(AppException):
    pass


class UserNotFoundException(AppException):
    pass


class CodeNotFoundException(AppException):
    pass


class CodeExpiredException(AppException):
    pass


class UnauthorizedException(AppException):
    pass


class InactiveUserException(AppException):
    pass


class InternalServerException(AppException):
    pass


class InvalidPasswordException(AppException):
    pass