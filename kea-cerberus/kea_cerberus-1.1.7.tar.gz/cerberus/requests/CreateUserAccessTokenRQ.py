

from cerberus.requests.BodyRQ import BodyRQ

class CreateUserAccessTokenRQ(BodyRQ):

    def __init__(self, email):
        self.__email = email

    def getEmail(self):
        return self.__email
