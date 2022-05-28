class SSOException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def output(self):
        return {"code": self.code, "msg": self.message, "data": {}}