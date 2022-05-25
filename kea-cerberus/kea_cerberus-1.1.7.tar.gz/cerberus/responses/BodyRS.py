

from cerberus.dtos.Error import Error

class BodyRS(dict):

    def __init__(self, success, error= None):
        self.__success = success
        self.__error = error
        dict.__init__(self, success=success, error=error)


    def getSuccess(self):
        return self.__success

    def getError(self):
        return self.__error

    def setSuccess(self, success):
        self.__success = success

    def setError(self, error):
        self.__error = error
