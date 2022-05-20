from functools import wraps

from marshmallow.exceptions import ValidationError

from rispack.errors import InvalidResponseError, InvalidRoleError, NotFoundError
from rispack.roles import AdminRole

from .request import Request
from .response import Response


def route(*args, **kwargs):
    role = kwargs.get("role", None)
    pin = kwargs.get("pin", None)

    if role and type(role) is not AdminRole:
        raise InvalidRoleError("role must be an AdminRole")

    def inner(func):
        @wraps(func)
        def wrapper(event, context):
            try:
                request = Request(event)

                if role and _role_does_not_match(request.auth, role):
                    return Response.forbidden(f"{role} was not found in current user")

                result = func(request)

                if not isinstance(result, Response):
                    raise InvalidResponseError(
                        "The return of a route must be a Response instance"
                    )

            except ValidationError as e:
                errors = _get_validation_errors(e.messages)
                result = Response.bad_request(errors)

            except InvalidRoleError:
                result = Response.bad_request("invalid role error")

            except InvalidResponseError:
                result = Response.internal_server_error("invalid response error")

            except NotFoundError as e:
                error = e.args[0]
                result = Response.not_found(error)

            except Exception:
                result = Response.internal_server_error()

            return result.to_dict()

        return wrapper

    has_attrs = role or pin

    # args[0] is the function itself when called
    # without parenthesis e.g. @route. This enables
    return inner if has_attrs else inner(args[0])


def _get_validation_errors(fields):
    errors = []
    for key, value in fields.items():
        errors.append(
            {
                "id": f"invalid_{key}",
                "message": value[0],
                "field": key,
            }
        )
    return errors


def _role_does_not_match(auth, role):
    if not auth:
        return False

    return auth.role is not role
