from cerberus.responses.BodyRS import BodyRS

class SessionRS(BodyRS):

    __session = ''

    def __init__(self, success, error=None):
        BodyRS.__init__(self, success, error)

    def getSession(self):
        return self.__session

    def setSession(self, session):
        self.__session = session
        self.update(session=session)
