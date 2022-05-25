from cerberus.responses.BodyRS import BodyRS

class LoginClientRS(BodyRS):

    __connection = ''

    def __init__(self, success, error=None):
        BodyRS.__init__(self, success, error)

    def getConnection(self):
        return self.__connection

    def setConnection(self, connection):
        self.__connection = connection
        self.update(connection=connection)
