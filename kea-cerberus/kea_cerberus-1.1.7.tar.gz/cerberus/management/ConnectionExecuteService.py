from cerberus.management.SessionManagerAbstractService import SessionManagerAbstractService
from abc import abstractmethod

class ConnectionExecuteService(SessionManagerAbstractService):

    def __init__(self, request):
        SessionManagerAbstractService.__init__(self, request)

    def beforeExecute(self, connection):
        pass

    @abstractmethod
    def execute(self, connection):
        pass


    def afterExecute(self, connection):
        pass
