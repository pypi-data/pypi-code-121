#encoding=utf-8
class APIError(Exception):
    def __init__(self, errCode, errorInfo):
        self.errorinfo = errorInfo
        self.errorCode = errCode

    def __str__(self):
        return '{}(ErrCode={})'.format(self.errorinfo, str(self.errorCode))

class ErrorCodeException(APIError):
    def __init__(self, errCode, errorInfo):
        super().__init__(errCode,errorInfo)

    def __str__(self):
        return 'ErrCode: {}, {}'.format(self.errorinfo, str(self.errorCode))