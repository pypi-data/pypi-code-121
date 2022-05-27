import json


class HabitatException(Exception):
    def __init__(self, message, key=None, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.key = key
        self.message = message

    def json(self):
        return json.dumps({"Error": {self.key: self.message}})


class ConnectionException(HabitatException):
    pass


class DataException(HabitatException):
    pass


class RequestException(HabitatException):
    pass


class ResponseException(HabitatException):
    pass
