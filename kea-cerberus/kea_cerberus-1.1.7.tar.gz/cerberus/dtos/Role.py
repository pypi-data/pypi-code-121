
class Role:

    __id = 0
    __description = ''

    def __init__(self, id, description):
        self.__id = id
        self.__description = description

    def getId(self):
        return self.__id

    def getDescription(self):
        return self.__description
