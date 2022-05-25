

class HeaderRQ:

    def __init__(self, token, languageCode, xTimestamp):
        self.__token = token
        self.__languageCode = languageCode
        self.__xTimestamp = xTimestamp

    def getToken(self):
        return self.__token

    def getLanguageCode(self):
        return self.__languageCode

    def getXTimestamp(self):
        return self.__xTimestamp
