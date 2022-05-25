

class Session(dict):

    def __init__(self, token, userId, active, authenticationType, roleId, connection, createdAt, updatedAt):
        self.__token = token
        self.__userId = userId
        self.__active = active
        self.__authenticationType = authenticationType
        self.__roleId = roleId
        self.__connection = connection
        self.__updatedAt = updatedAt
        self.__createdAt = createdAt
        dict.__init__(self, token=token, userId=userId, active = active, authenticationType=authenticationType, roleId= roleId, connection = connection, createdAt=str(createdAt),updatedAt=str(updatedAt))

    def getToken(self):
        return self.__token

    def getUserId(self):
        return self.__userId

    def getActive(self):
        return self.__active

    def getAuthenticationType(self):
        return self.__authenticationType

    def getRoleId(self):
        return self.__roleId

    def getConnection(self):
        return self.__connection

    def setConnection(self, connection):
        self.__connection = connection

    def getUpdatedAt(self):
        return self.__updatedAt

    def getCreatedAt(self):
        return self.__createdAt
