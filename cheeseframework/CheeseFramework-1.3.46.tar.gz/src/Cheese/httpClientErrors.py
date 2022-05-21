#cheese

from Cheese.httpError import HTTPError

class BadRequest(HTTPError):
    def __init__(self, description):
        super().__init__(description, "Bad Request", 400)

class Unauthorized(HTTPError):
    def __init__(self, description):
        super().__init__(description, "Unauthorized", 401)

class PaymentRequired(HTTPError):
    def __init__(self, description):
        super().__init__(description, "Payment Required", 402)

class Forbidden(HTTPError):
    def __init__(self, description):
        super().__init__(description, "Forbidden", 403)

class NotFound(HTTPError):
    def __init__(self, description):
        super().__init__(description, "Not Found", 404)

class MethodNotAllowed(HTTPError):
    def __init__(self, description):
        super().__init__(description, "Method Not Allowed", 405)

class NotAcceptable(HTTPError):
    def __init__(self, description):
        super().__init__(description, "Not Acceptable", 406)


class Conflict(HTTPError):
    def __init__(self, description):
        super().__init__(description, "Conflict", 409)

class ImTeaPot(HTTPError):
    def __init__(self, description):
        super().__init__(description, "I'm teapot", 418)