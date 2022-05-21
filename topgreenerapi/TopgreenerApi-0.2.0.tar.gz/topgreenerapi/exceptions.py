
class TuyaException(Exception):
    def __init__(self, message, errorCode):
        super().__init__(message)

        self.errorCode = errorCode
