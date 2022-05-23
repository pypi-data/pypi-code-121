from django.utils.translation import gettext_lazy as _

from pfx.pfxcore.http import JsonResponse

from .shortcuts import delete_token_cookie, f


class APIError(Exception):
    def __init__(self, message, status=400, delete_cookie=False, **kwargs):
        self.status = status
        self.data = dict(message=message, **kwargs)
        self.delete_cookie = delete_cookie

    @property
    def response(self):
        res = JsonResponse(self.data, status=self.status)
        if self.delete_cookie:
            return delete_token_cookie(res)
        return res


class JsonErrorAPIError(APIError):
    def __init__(self, json_error, status=422, **kwargs):
        super().__init__(
            f(_("JSON Malformed {}").format(str(json_error))),
            status=status, **kwargs)


class ModelNotFoundAPIError(APIError):
    def __init__(self, model, status=404, **kwargs):
        super().__init__(
            f(_("{model} not found."), model=model._meta.verbose_name),
            status=status, **kwargs)


class ModelValidationAPIError(APIError):
    def __init__(
            self, errors, status=422, delete_cookie=False, **kwargs):
        self.status = status
        self.data = errors
        self.delete_cookie = delete_cookie


class RelatedModelNotFoundAPIError(ModelValidationAPIError):
    def __init__(
            self, field, model, status=422, delete_cookie=False, **kwargs):
        super().__init__({field: [
            f(_("{model} not found."), model=model._meta.verbose_name)]},
            status=status, delete_cookie=delete_cookie, **kwargs)


class AuthenticationError(APIError):
    def __init__(self, message=None, status=401, **kwargs):
        super().__init__(
            f(message or _("Authentication Error")),
            status=status, **kwargs)


class UnauthorizedError(APIError):
    def __init__(self, **kwargs):
        super().__init__(
            f(_("Unauthorized")),
            status=401, **kwargs)


class ForbiddenError(APIError):
    def __init__(self, **kwargs):
        super().__init__(
            f(_("Forbidden")),
            status=403, **kwargs)


class NotFoundError(APIError):
    def __init__(self, **kwargs):
        super().__init__(
            f(_("Resource not found")),
            status=404, **kwargs)
