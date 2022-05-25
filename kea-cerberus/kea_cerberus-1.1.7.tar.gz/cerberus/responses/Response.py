

class Response(dict):

    def __init__(self, headerRS, bodyRS):
        self.__headerRS = headerRS
        self.__bodyRS = bodyRS
        dict.__init__(self, headerRS=headerRS, bodyRS=bodyRS)

    def getHeaderRS(self):
        return self.__headerRS

    def getBodyRS(self):
        return self.__bodyRS
