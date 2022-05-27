"""
Gets the name of this DataSourceProfile.
The name used to reference this datasource.

:return: The name of this DataSourceProfile.
:rtype: str
"""
class ApiException(Exception):
    def __init__(self, message=None, innerException=None, statusCode=None):
        self._message = None
        self._innerException = None
        self._statusCode = None

        if message is not None:
            self._message = message
        if innerException is not None:
            self._innerException = innerException
        if statusCode is not None:
            self._statusCode = statusCode

        if self._innerException != None:
            super().__init__(self._message, self._innerException)
        else:
            super().__init__(self._message)

    @property
    def message(self):
        return self._message
    @message.setter
    def message(self, message):
        self._message = message

    @property
    def innerException(self):
        return self._innerException
    @innerException.setter
    def innerException(self, inner_exception):
        self._innerException = inner_exception

    @property
    def statusCode(self):
        return self._statusCode
    @statusCode.setter
    def statusCode(self, status_code):
        self._statusCode = status_code

