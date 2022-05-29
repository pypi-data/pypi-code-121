import logging
import traceback
from pathlib import Path
from inspect import getmembers, isclass
from functools import partial
from logging import Logger
from typing import Optional, Type, Union, Any

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, PlainTextResponse
from starlette.requests import Request
from starlette.exceptions import HTTPException

from .base import Settings, ApiMember
from .tools import title_to_snake
from .filesystem import module_from_path
from .events import Event
from .tortoise.base import EmapiDbModel
from .endpoints import (
	SingleEventEndpoint,
	MultiEventEndpoint,
	MultiModelEndpoint,
	SingleModelEndpoint,
	ApiEndpoint,
	HTTPEndpoint,
)
from .templates import Swagger
from .openapi import EmapiOpenApiSchema
from .responses import JsonResponse


def is_server_object(module, obj: Any) -> bool:
	if not isclass(obj):
		return False
	if getattr(obj, "__module__", None) != module:
		return False
	if issubclass(obj, HTTPEndpoint):
		return True
	if not issubclass(obj, ApiMember):
		return False
	if obj in (EmapiDbModel, Event):
		return False
	if obj.Meta.abstract:
		return False
	return True


class Server(Starlette):
	openapi_f_name = "oapi.yaml"

	def __init__(
		self, settings: Union[Type[Settings], Settings], log: Optional[Logger] = None, openapi: bool = False, **kwargs,
	):
		self.settings = settings
		self.logger = log or logging.getLogger()
		self.objects = {}
		if self.settings.debug:
			self.logger.setLevel(logging.DEBUG)
		super().__init__(**kwargs)
		self.import_apis()
		if openapi:
			self.add_openapi()
		self.logger.info("Registered paths:")
		for r in self.router.routes:
			self.logger.info(f"{r.path} : {r.endpoint}")

	def import_apis(self) -> None:
		for d in ("events", "models"):
			apis_path = Path.cwd() / "app" / d
			for path in apis_path.rglob("*.py"):
				if "__pycache__" in path.parts:
					continue
				self.register_api(path)

	def register_api(self, path: Path) -> None:
		self.logger.info(f"Registering objects from {path}")
		api, api_module_name, pkg = module_from_path(path)
		for obj_name, obj in getmembers(api, predicate=partial(is_server_object, api.__name__)):
			if obj.Meta.api_excluded:
				continue
			base_path = f"/api/v{obj.Meta.version}"
			if obj.Meta.base_model:
				base_name = obj.Meta.base_model.__name__.lower()
				base_path += f"/{base_name}"
				if obj.Meta.need_resource:
					base_path += f"/{{{obj.Meta.base_model.describe()['pk']['name']}}}"
			if issubclass(obj, EmapiDbModel):
				self.register_model(base_path, obj)
			elif issubclass(obj, Event):
				self.register_event(base_path, obj)
			elif issubclass(obj, HTTPEndpoint):
				self.register_custom_endpoint(obj_name, obj, base_path=base_path)
			else:
				continue

	def register_model(self, base_path: str, obj: Type[EmapiDbModel]) -> None:
		obj_name = obj.__name__.lower()
		api_path = f"{base_path}/{obj_name}"

		for obj_name, custom_endpoint in getmembers(obj, predicate=partial(is_server_object, obj.__module__)):
			custom_endpoint.obj = obj
			self.register_custom_endpoint(obj_name, custom_endpoint, base_path=f"{api_path}s")

		if obj.Meta.multi:
			self.add_api_route(f"{api_path}s", MultiModelEndpoint, obj, excluded_methods=("put",) if obj.generated_id else tuple())

		if obj.generated_id:
			self.add_api_route(api_path, SingleModelEndpoint, obj, excluded_methods=tuple(set(obj.Meta.methods) - {"post"}))

		api_path += f"/{{{obj.pk_field['name']}}}"
		self.add_api_route(api_path, SingleModelEndpoint, obj, excluded_methods=("post", "put") if obj.generated_id else tuple())

		self.objects.setdefault(obj.__class__.__name__, obj)

	def register_event(self, base_path: str, obj: Type[Event]) -> None:
		obj_name = obj.__name__.lower()
		api_path = f"{base_path}/{obj_name}"

		if obj.Meta.multi:
			self.add_api_route(f"{api_path}s", MultiEventEndpoint, obj)

		self.add_api_route(api_path, SingleEventEndpoint, obj)

		self.objects.setdefault(obj.Meta.base_model.__class__.__name__, obj.Meta.base_model)
		self.objects.setdefault(obj.__class__.__name__, obj)
		for outcome in obj.Meta.outcomes:
			self.objects.setdefault(outcome.__class__.__name__, outcome)

	def register_custom_endpoint(self, cls_name: str, endpoint: Type[HTTPEndpoint], base_path: str = "") -> None:
		self.add_route(f"{base_path}/{cls_name.lower()}", endpoint)

	def add_api_route(
		self,
		path: str,
		base_endpoint: Type[ApiEndpoint],
		obj: Type[Union[Event, EmapiDbModel]],
		excluded_methods: Optional[tuple[str]] = tuple(),
	) -> None:
		attrs = {
			k: v
			for k, v in base_endpoint.__dict__.items()
			if k not in ApiMember.Meta.methods or (k in obj.Meta.methods and k not in excluded_methods)
		}
		attrs.update({"obj": obj, "path": path})
		endpoint = type(f"{obj.__name__}{base_endpoint.__name__}", base_endpoint.__bases__, attrs)
		self.add_route(path, endpoint)

	def add_openapi(self) -> None:
		schema = EmapiOpenApiSchema(app=self)
		# app_name=self.settings.app_name
		for version, info in schema.from_routes():
			self.add_openapi_endpoints(version, info)

	def add_openapi_endpoints(self, version: int, openapi_specs: str) -> None:
		swag_html = Swagger(openapi_url=f"/api/v{version}/{self.openapi_f_name}").render()

		async def openapi(request: Request) -> PlainTextResponse:
			return PlainTextResponse(openapi_specs, media_type="application/yaml")

		self.add_route(f"/api/v{version}/{self.openapi_f_name}", openapi)

		async def swagger_ui_html(request: Request) -> HTMLResponse:
			return HTMLResponse(swag_html)

		self.add_route(f"/api/v{version}/docs", swagger_ui_html, include_in_schema=False)


def http_exception(request: Request, exc: HTTPException) -> JsonResponse:
	"""Handled error response from the server"""
	return JsonResponse(
		{"errors": [{"description": str(exc) or exc.__class__.__name__, "detail": getattr(exc, "detail", None)}]},
		status_code=exc.status_code,
	)


def generic_exception(request: Request, exc: HTTPException) -> JsonResponse:
	"""Un-Handled error response from the server"""
	return JsonResponse({"error": str(exc), "traceback": "".join(traceback.format_tb(exc.__traceback__))}, status_code=500)
