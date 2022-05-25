from cerberus.responses.BodyRS import BodyRS

class CreateUserRS(BodyRS):

    def __init__(self, success, error=None):
        BodyRS.__init__(self, success, error)

    def getUser(self):
        return self.__user

    def setUser(self, user):
        self.__user = user
        self.update(user=user)
