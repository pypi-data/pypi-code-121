class SessionManagerAbstractService():

    def __init__(self, request):
        self.__request = request

    def getRequest(self):
        return self.__request
