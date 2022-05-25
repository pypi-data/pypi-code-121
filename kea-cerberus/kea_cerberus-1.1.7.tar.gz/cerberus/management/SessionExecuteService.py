from cerberus.management.SessionManagerAbstractService import SessionManagerAbstractService
from abc import abstractmethod

class SessionExecuteService(SessionManagerAbstractService):

    def __init__(self, request):
        SessionManagerAbstractService.__init__(self, request)


    def beforeExecute(self, session):
        pass

    @abstractmethod
    def execute(self, session):
        pass


    def afterExecute(self, session):
        pass
