from starlette.authentication import AuthenticationError

from .base import FormattedError


class HTTPAuthenticationError(AuthenticationError):
	status_code = 401
	message = "Authentication Error"


class NoAuthHeader(HTTPAuthenticationError):
	message = "Missing Authorization Header"


class WrongAuthScheme(FormattedError, AuthenticationError):
	status_code = 406
	message_template = "Authorization '{scheme}' not accepted"


class ExpiredToken(HTTPAuthenticationError):
	status_code = 403
	message = "Token has expired or missing"


class InvalidToken(HTTPAuthenticationError):
	status_code = 403
	message = "Bearer token not valid for auth"


class InvalidUserToken(FormattedError, AuthenticationError):
	status_code = 403
	message_template = "Invalid bearer token for user {user}"
