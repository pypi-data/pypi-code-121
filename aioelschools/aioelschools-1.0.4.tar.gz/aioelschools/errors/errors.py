from ..utils.code_exception import CodeException


class APIError(CodeException):
    def __str__(self, **kwargs):
        return self.args[0]
