from typing import Optional, Union, Type
from yaml import dump as dump_yaml
from itertools import groupby
from inspect import getdoc, signature

from starlette.routing import Route
from starlette.middleware.authentication import AuthenticationMiddleware

from .events import Event, Outcome
from .tortoise.base import EmapiDbModel
from .endpoints import ApiEndpoint, EventEndpoint, SingleEndpoint


class EmapiOpenApiSchema:
	def __init__(self, app: Type["Server"], openapi_version: Optional[str] = "3.0.0", title: Optional[str] = None):
		self.app = app
		self.title = title
		self.openapi_version = openapi_version
		self.errors = self.read_app_error_handlers()
		self.schemas = self.build_schemas()

	def build_schemas(self) -> dict:
		ret = {}
		for obj in self.app.objects.values():
			ret.setdefault(obj.Meta.version, {})
			ret[obj.Meta.version][obj.__name__] = self.render_obj(obj)
		return ret

	def read_app_error_handlers(self) -> dict:
		ret = {}
		for exc, handler in self.app.exception_handlers.items():
			try:
				content_typ = signature(handler).return_annotation.media_type
			except:
				content_typ = "text/plain"

			ret[exc] = {
				"$ref": f"#/components/schemas/{exc.__name__}",
				"description": " ".join((getdoc(handler), getdoc(exc), str(exc))),
				"content_type": content_typ,
				"handler": handler,
				"status_code": getattr(exc, "status_code", "500"),
			}
		return ret

	def add_exceptions(self, base: dict):
		for exc, data in self.errors.items():
			base["components"]["schemas"][exc.__name__] = self.format_exc(exc, data["description"])
			base["components"]["responses"][exc.__name__] = {
				data["content_type"]: {"schema": {"$ref": data["$ref"]}, "description": data["description"],}
			}

	def add_auth(self, base: dict):
		for middleware in self.app.user_middleware:
			if middleware.cls is AuthenticationMiddleware:
				auth_name = middleware.options["backend"].__class__.__name__
				base["components"]["securitySchemes"][auth_name] = {
					"type": middleware.options["backend"].type,
					"scheme": middleware.options["backend"].schema,
					"bearerFormat": "JWT",
				}
				base["security"].append({auth_name: []})

	def base_openapi_dict(self, version: int) -> dict:
		base = {
			"openapi": self.openapi_version,
			"info": {
				"title": self.title or self.app.settings.app_name,
				"version": str(version),
				"description": getdoc(self.app),
				"contact": {"name": self.app.settings.get("owner", ""), "email": self.app.settings.get("maintainer", ""),},
			},
			"servers": [
				{
					"url": "/",
					"description": f"{self.app.settings.get('ecosystem', '')} | {self.app.settings.get('environment', '')}",
				}
			],
			"paths": {},
			"components": {"responses": {}, "securitySchemes": {}, "schemas": self.schemas.get(version, {})},
			"security": [],
		}
		self.add_exceptions(base)
		self.add_auth(base)
		return base

	@staticmethod
	def format_exc(exc, description: str) -> dict:
		return {
			"properties": {
				"errors": {
					"items": {
						"properties": {
							"description": {"example": str(exc), "type": "string"},
							"detail": {"example": "Reason the server returned the error", "type": "string"},
						},
						"type": "object",
					},
					"type": "array",
				}
			},
			"type": "object",
			"description": description,
		}

	@staticmethod
	def format_parameter(param: str, typ: str, obj: Union[Type[EmapiDbModel], Type[Event]]) -> dict:
		obj_info = obj.describe()
		if typ == "path":
			api_name = param
			if obj.Meta.base_model and param.replace("_id", "") != obj_info["name"].replace("models.", "").lower():
				base_obj_info = obj.Meta.base_model.describe()
				param_data = base_obj_info["pk"]
			else:
				param_data = obj_info["pk"]
		else:
			api_name = f"filter[{param}]"
			param_data = obj_info["filters"][param]
		return {
			"description": param_data["description"],
			"in": typ,
			"name": api_name,
			"required": typ == "path",
			"schema": param_data,
		}

	def method_request_body(self, endpoint: ApiEndpoint) -> dict:
		return {"content": self.render_payload(endpoint, body=True)}

	@classmethod
	def render_payload(cls, endpoint: ApiEndpoint, body=False) -> dict:
		objs = (endpoint.obj,)
		if issubclass(endpoint, EventEndpoint):
			if not body:
				objs = endpoint.obj.Meta.outcomes
			else:
				objs = (endpoint.obj,)
		if not objs:
			return {}
		elif len(objs) == 1:
			data = {"$ref": f"#/components/schemas/{objs[0].__name__}"}
		else:
			data = {"anyOf": [{"$ref": f"#/components/schemas/{obj.__name__}"} for obj in objs]}
		return {"application/json": {"schema": data}}

	@classmethod
	def render_obj(cls, obj: Union[Type[EmapiDbModel], Type[Event], Type[Outcome]]) -> dict:
		obj_info = obj.describe()
		ret = {
			"description": obj_info["description"],
			"type": "object",
			"properties": {
				"id": {"name": obj_info["pk"]["name"], "description": obj_info["pk"]["description"], "type": "string"},
				"type": {"example": obj_info["name"], "type": "string"},
				"attributes": {"type": "object", "properties": obj_info["properties"]},
			},
		}
		if obj_info.get("relationships"):
			ret["properties"]["relationships"] = {
				"type": "object",
				"properties": {
					rel_name: {
						"type": "object",
						"properties": {
							"data": {
								"type": "object",
								"properties": {
									"type": {"example": rel_info["name"], "type": "string"},
									"id": {"name": rel_info["pk"]["name"], "description": rel_info["pk"]["description"], "type": "string"},
								},
							}
						},
					}
					for rel_name, rel_info in obj_info["relationships"].items()
				},
			}
		return ret

	def method_responses(self, endpoint: Type[ApiEndpoint], http_mth: str) -> dict:
		obj = endpoint.obj
		if issubclass(endpoint, EventEndpoint):
			obj = endpoint.obj.Meta.base_model
		ret = {
			"401": {"$ref": "#/components/responses/Unauthorized"},
			"404": {"description": f"A {obj.__name__} with the specified ID was not found."},
		}
		if http_mth != "delete":
			ret["200"] = {"content": self.render_payload(endpoint), "description": "Successful response"}
		else:
			ret["204"] = {"description": "The resource was deleted successfully."}

		for error in self.errors.values():
			ret[str(error["status_code"])] = {"$ref": error["$ref"]}

		return ret

	@staticmethod
	def get_version(route: Route) -> Optional[int]:
		if isinstance(route, Route) and issubclass(route.endpoint, ApiEndpoint):
			if route.endpoint.obj:
				return route.endpoint.obj.Meta.version
		return 0

	def from_routes(self) -> dict[int, str]:
		for version, routes in groupby(sorted(self.app.router.routes, key=self.get_version), key=self.get_version):
			if not version:
				continue
			openapi_schema = self.base_openapi_dict(version)
			for route in routes:
				openapi_schema["paths"][route.path] = {}
				for mth_info in route.endpoint.methods_info():
					pars = []
					for p in route.param_convertors:
						pars.append(self.format_parameter(p, "path", route.endpoint.obj))
					if mth_info["name"] == "get" and not issubclass(route.endpoint, SingleEndpoint):
						for p in route.endpoint.obj.describe().get("filters", []):
							pars.append(self.format_parameter(p, "query", route.endpoint.obj))
					mth_info["parameters"] = pars
					if mth_info["name"] in ("post", "put", "patch"):
						mth_info["requestBody"] = self.method_request_body(route.endpoint)
					mth_info["responses"] = self.method_responses(route.endpoint, mth_info["name"])
					openapi_schema["paths"][route.path][mth_info["name"]] = mth_info
			yield version, dump_yaml(openapi_schema)
