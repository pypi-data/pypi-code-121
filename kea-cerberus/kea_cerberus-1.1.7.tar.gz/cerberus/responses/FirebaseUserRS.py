from cerberus.responses.BodyRS import BodyRS

class FirebaseUserRS(BodyRS):

    def __init__(self, success, error=None):
        BodyRS.__init__(self, success, error)
