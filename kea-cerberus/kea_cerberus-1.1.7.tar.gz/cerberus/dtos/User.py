class User(dict):

    def __init__(self, id, createdAt, updatedAt):
        self.__id = id
        self.__updatedAt = updatedAt
        self.__createdAt = createdAt
        dict.__init__(self, id=id, createdAt=str(createdAt), updatedAt=str(updatedAt))

    def getId(self):
        return self.__id

    def getUpdatedAt(self):
        return self.__updatedAt

    def getCreatedAt(self):
        return self.__createdAt
