from tornado.web import HTTPError
from tornado_middleware import MiddlewareHandler
from typing import Awaitable, Optional


class LoginMiddlewareHandler(MiddlewareHandler):
    """
    A simple login middleware handler,
    use header "Authorization" and need a function `login(username: str, password: str) -> Awaitable[bool]`
    """

    async def login(self, username: str, password: str) -> Awaitable[bool]:
        raise NotImplementedError("define a login function")

    async def _middleware_login(self, next):
        import base64

        if "Authorization" not in self.request.headers:
            raise HTTPError(403, '"Authorization" header was not set')

        auth = self.request.headers["Authorization"]
        if not auth.startswith("Basic "):
            raise HTTPError(
                400, '"Authorization" header must be a Basic authentication'
            )

        username, password = (
            base64.b64decode(auth.split(" ")[1].encode()).decode().split(":")
        )
        if await self.login(username, password):
            await next()
        else:
            raise HTTPError(401)


class JSONSchemaValidationMiddleware(MiddlewareHandler):
    """
    JSONSchema Validator middleware if method is different to 'HEAD' or 'GET',
    schema must be set on `self.schema`
    """

    schema: Optional[dict] = None

    async def _middleware_validation(self, next):
        import jsonschema
        from tornado.escape import json_decode
        from jsonschema.exceptions import ValidationError
        from json.decoder import JSONDecodeError

        if self.request.method not in self.omitted_methods:
            if "Content-Type" not in self.request.headers:
                raise HTTPError(400, "You must sent a body")

            try:
                data = json_decode(self.request.body)
            except JSONDecodeError:
                raise HTTPError(500, "The body is not a JSON document")
            else:
                try:
                    jsonschema.validate(data, self.schema)
                except ValidationError as err:
                    raise HTTPError(400, f"JSON schema is not valid: {err.message}")

        await next()
