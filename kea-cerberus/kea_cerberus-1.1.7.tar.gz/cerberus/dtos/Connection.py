
class Connection(dict):

    __token = ''
    __clientId = 0
    __active = False
    __createdAt = ''
    __updatedAt = ''

    def __init__(self, token, clientId, active, createdAt, updatedAt):
        self.__token = token
        self.__clientId = clientId
        self.__active = active
        self.__createdAt = createdAt
        self.__updatedAt = updatedAt
        dict.__init__(self, token=token, clientId=clientId, active=active, createdAt=str(createdAt),updatedAt=str(updatedAt))

    def getToken(self):
        return self.__token

    def getClientId(self):
        return self.__clientId

    def getActive(self):
        return self.__active

    def getUpdatedAt(self):
        return self.__updatedAt

    def getCreatedAt(self):
        return self.__createdAt
