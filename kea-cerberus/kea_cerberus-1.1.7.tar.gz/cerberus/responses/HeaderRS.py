

class HeaderRS(dict):

    __token = ''
    __updatedAt = ''
    __createdAt = ''

    def __init__(self, token=None, createdAt=None, updatedAt=None):
        self.__token = token
        self.__createdAt = createdAt
        self.__updatedAt = updatedAt
        dict.__init__(self, token=token, createdAt=str(createdAt), updatedAt=str(updatedAt))

    def getToken(self):
        return self.__token

    def getUpdatedAt(self):
        return self.__updatedAt

    def getCreatedAt(self):
        return self.__createdAt
