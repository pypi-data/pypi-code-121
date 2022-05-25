from cerberus.responses.BodyRS import BodyRS

class CreateUserAccessTokenRS(BodyRS):

    def __init__(self, success, error=None):
        BodyRS.__init__(self, success, error)

    def getSecurityHash(self):
        return self.__securityHash

    def setSecurityHash(self, securityHash):
        self.__securityHash = securityHash
        self.update(securityHash=securityHash)
