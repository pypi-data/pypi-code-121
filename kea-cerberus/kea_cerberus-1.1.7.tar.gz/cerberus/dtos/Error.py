
class Error(dict):

    def __init__(self, code, message, httpCode='200', type = None):
        self.__code = code
        self.__message = message
        self.__httpCode = httpCode
        self.__type = type
        dict.__init__(self, code=code, message=message, httpCode=httpCode)


    def getCode(self):
        return self.__code

    def getMessage(self):
        return self.__message
