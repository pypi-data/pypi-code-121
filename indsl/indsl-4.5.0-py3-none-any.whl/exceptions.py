class UserException(Exception):
    pass


class UserValueError(ValueError, UserException):
    pass


class UserTypeError(TypeError, UserException):
    pass


class UserRuntimeError(RuntimeError, UserException):
    pass
