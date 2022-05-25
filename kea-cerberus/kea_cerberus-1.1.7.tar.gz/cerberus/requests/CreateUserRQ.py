

from cerberus.requests.BodyRQ import BodyRQ

class CreateUserRQ(BodyRQ):

    def __init__(self, securityToken, username, token, roleId, authenticationTypeId):
        self.__securityToken = securityToken
        self.__username = username
        self.__token = token
        self.__roleId = roleId
        self.__authenticationTypeId = authenticationTypeId

    def getSecurityToken(self):
        return self.__securityToken

    def getUserName(self):
        return self.__username

    def getToken(self):
        return self.__token

    def getRoleId(self):
        return self.__roleId

    def getAuthenticationTypeId(self):
        return self.__authenticationTypeId
