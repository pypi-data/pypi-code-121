import os


class Error(Exception):
    def __init__(self, message="something went wrong", code=500):
        Exception.__init__(self)

        self.message = message
        self.code = code

        assert(self.code > 399 and self.code < 600)

    def _debugging(self):
        debug = os.environ.get("APP_DEBUG")

        return debug and (debug.lower() == "true" or debug == "1")

    def json(self):
        msg = "something went wrong" if self.code > 499 and not self._debugging() else self.message

        body = {
            "code": self.code,
        }

        if type(msg) is dict:
            for k, v in msg.items():
                body[k] = v
        else:
            body["message"] = msg

        return body


class NotFound(Error):
    def __init__(self, resource):
        super(NotFound, self).__init__(f"{resource}: not found", 404)


class Conflict(Error):
    def __init__(self, resource):
        super(Conflict, self).__init__(f"{resource}: already exists", 409)


class BadRequest(Error):
    def __init__(self, message):
        super(BadRequest, self).__init__(message, 400)


class MethodNotAllowed(Error):
    def __init__(self, method):
        super(MethodNotAllowed, self).__init__(f"{method} not allowed", 405)


class Unauthorized(Error):
    def __init__(self, scope):
        super(Unauthorized, self).__init__(f"unauthorized: {scope} scope is required", 401)
