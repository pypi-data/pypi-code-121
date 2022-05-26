
class DiscordClientError(Exception):
    pass

class InvalidParams(Exception):
    pass

class ResponseError(DiscordClientError):
    pass


class BadRequest(ResponseError):
    pass


class Unauthorized(ResponseError):
    pass


class Forbidden(ResponseError):
    pass


class NotFound(ResponseError):
    pass


class TooManyRequests(ResponseError):
    pass


class InternalServerError(ResponseError):
    pass


class UnknownError(DiscordClientError):
    pass


api_errors = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    429: TooManyRequests,
    500: InternalServerError
}















