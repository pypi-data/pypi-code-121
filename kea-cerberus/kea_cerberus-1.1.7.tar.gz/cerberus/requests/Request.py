

class Request:

    def __init__(self, headerRQ, bodyRQ=None):
        self.__headerRQ = headerRQ
        self.__bodyRQ = bodyRQ

    def getHeaderRQ(self):
        return self.__headerRQ

    def getBodyRQ(self):
        return self.__bodyRQ
