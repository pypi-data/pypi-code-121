
class SecurityHash(dict):
    AUTH_TOKEN = 1
    CREATE_USER_TOKEN = 2

    def __init__(self, token, typeId, used, active):
        self.__token = token
        self.__typeId = typeId
        self.__used = used
        self.__active = active
        dict.__init__(self, token=token, typeId=typeId, used = used, active=active)

    def getToken(self):
        return self.__token

    def getTypeId(self):
        return self.__typeId

    def getUsed(self):
        return self.__used

    def getActive(self):
        return self.__active
