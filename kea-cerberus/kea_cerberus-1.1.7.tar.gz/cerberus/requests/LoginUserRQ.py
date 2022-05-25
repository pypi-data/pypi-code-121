

from cerberus.requests.BodyRQ import BodyRQ

class LoginUserRQ(BodyRQ):

    def __init__(self, username, token, authenticationTypeId):
        self.__username = username
        self.__token = token
        self.__authenticationTypeId = authenticationTypeId

    def getUserName(self):
        return self.__username

    def getToken(self):
        return self.__token

    def getAuthenticationTypeId(self):
        return self.__authenticationTypeId
