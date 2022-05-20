import json
from dataclasses import dataclass
from typing import Any, Dict, Union

from rispack.errors import InvalidRoleError
from rispack.roles import AdminRole


@dataclass
class Auth:
    id: str
    role: AdminRole = None
    fullname: str = None
    email: str = None


@dataclass
class Request:
    event: Dict[str, Any]
    auth: Auth = None
    body: Union[Dict[str, Any], str] = None
    pathparams: Dict[str, Any] = None
    queryparams: Dict[str, Any] = None
    headers: Dict[str, str] = None
    identity: Dict[str, Any] = None

    def __post_init__(self):
        self.auth = self._load_auth()
        self.body = self._load_body()
        self.pathparams = self._load_path()
        self.queryparams = self._load_query()
        self.headers = self._load_headers()
        self.identity = self._load_identity()
        self.params = self._load_params()

    def _load_auth(self):
        context = self.event.get("requestContext") or {}
        authorizer = context.get("authorizer") or None

        if authorizer:
            if authorizer.get("role"):
                try:
                    authorizer["role"] = AdminRole(authorizer["role"])
                except ValueError as e:
                    raise InvalidRoleError(e)

            return Auth(**authorizer)

    def _load_body(self):
        body = self.event.get("body") or ""

        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body

    def _load_path(self):
        path = self.event.get("pathParameters") or {}
        return path

    def _load_query(self):
        query = self.event.get("queryStringParameters") or {}
        return query

    def _load_headers(self):
        headers = self.event.get("headers") or {}
        return headers

    def _load_identity(self):
        context = self.event.get("requestContext") or {}
        identity = context.get("identity") or {}
        return identity

    def _load_params(self):
        return {**self.queryparams, **self.pathparams}
