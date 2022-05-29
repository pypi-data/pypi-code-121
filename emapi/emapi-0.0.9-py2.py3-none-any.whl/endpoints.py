import re
from operator import itemgetter
from urllib.parse import unquote, unquote_plus
from typing import List, Optional, Union, Iterable
from json import JSONDecodeError
from inspect import getmembers, getmro, isfunction, getdoc

from starlette.endpoints import HTTPEndpoint
from starlette.responses import Response
from starlette.requests import Request
from starlette.middleware.cors import ALL_METHODS
from tortoise.exceptions import IntegrityError

from .events import Event, Outcome
from .responses import JsonResponse
from .models import EmapiDbModel
from .exceptions.base import BaseEmapiError
from .exceptions.models import ModelConflict, ModelNotFound


EXCLUDED_MODEL_INFO = ("app", "table", "python_type", "db_column", "db_field_types", "abstract", "docstring")

EXCLUDED_EVENT_INFO = tuple()


def format_obj_data(obj: dict) -> dict:
	ret = {}
	for k, v in obj.items():
		if k in EXCLUDED_MODEL_INFO or k in EXCLUDED_EVENT_INFO:
			continue
		elif isinstance(v, dict):
			ret[k] = format_obj_data(v)
		elif isinstance(v, list):
			ret[k] = [format_obj_data(e) for e in v]
		else:
			ret[k] = v
	return ret


def is_hhtp_method(m):
	return isfunction(m) and m.__name__.upper().split("_")[0] in ALL_METHODS


class ApiEndpoint(HTTPEndpoint):
	obj = None

	filter_re = re.compile(r"filter\[(.*)]")

	@staticmethod
	async def get_json(request: Request, ignore_erros: bool = False) -> dict:
		try:
			return await request.json()
		except JSONDecodeError:
			if ignore_erros:
				return {}
			raise

	@classmethod
	def format_model(cls, obj: EmapiDbModel, with_attributes: Optional[bool] = True) -> dict:
		data = obj.dict(for_api_response=True)
		meta = obj.describe()
		ret = {"id": data[meta["pk"]["name"]], "type": meta["name"]}
		if with_attributes:
			ret["attributes"] = data
		return ret

	@staticmethod
	def format_outcome(outcome: Outcome) -> dict:
		out = outcome.dict()
		out.pop("id")
		return {"id": outcome.id, "type": f"{outcome.__module__}.{outcome.__class__.__name__}", "attributes": out}

	@classmethod
	async def get_model_relationships(cls, obj: EmapiDbModel, recursive: Optional[bool] = False) -> dict:
		ret = {}
		relationships = await obj.get_relationships()
		for rel_name, rels in relationships.items():
			if rel_name in obj.Meta.api_excluded_fields:
				continue
			out_rel = []
			for rel in rels:
				rel_data = cls.format_model(rel, with_attributes=recursive)
				if recursive:
					rel_rels = await cls.get_model_relationships(rel, recursive=recursive)
					if rel_rels:
						rel_data["relationships"] = rel_rels
				out_rel.append(rel_data)
			ret[rel_name] = out_rel
		return ret

	async def options(self, request: Request) -> Response:
		return JsonResponse({"resource": self.resource_info(), "methods": list(self.methods_info())})

	@classmethod
	def resource_info(cls: "ApiEndpoint") -> dict:
		resource_props = format_obj_data(cls.obj.describe())
		return {
			"type": resource_props["type"],
			"name": cls.obj.__name__.lower(),
			"properties": resource_props["properties"],
			"id": resource_props["pk"],
			"description": resource_props["description"],
		}

	@classmethod
	def methods_info(cls: "ApiEndpoint") -> dict:
		for meth_name, meth in getmembers(cls, predicate=is_hhtp_method):
			if meth_name == "head":
				continue
			if meth_name == "options":
				tags = ["Introspection"]
			else:
				tags = set(m.__name__ for m in cls.obj.hierarchy())
				if issubclass(cls.obj, Event):
					tags.remove(cls.obj.__name__)
					for c in getmro(cls.obj)[1:]:
						if c.Meta.abstract:
							break
						tags.add(c.__name__)
				for module_part in cls.obj.__module__.split("."):
					if module_part in ("models", "events", "app"):
						continue
					if module_part.endswith("s") and module_part[:-1].title() in tags:
						continue
					tags.add(module_part.title())
			yield {"description": getdoc(meth), "tags": list(tags), "summary": getdoc(cls.obj), "name": meth_name}

	def read_jsonapi_query(self, request: Request) -> dict:
		try:
			return {
				self.filter_re.search(p).group(1): unquote_plus(unquote(v)).replace("null", "") or None
				for p, v in request.query_params.items()
			}
		except AttributeError:
			raise BaseEmapiError(400, f"One of the given filters is not jsonapi-compliant: {list(request.query_params.keys())}")

	def match_query_object(self, query: dict, only_indexed: Optional[bool] = True) -> None:
		if not getattr(self, "obj", None):
			return
		obj_metadata = self.obj.describe()
		indexed = obj_metadata.get("filters", {})
		attributes = obj_metadata.get("properties", {})
		invalid = set(query) - (set(attributes) if not only_indexed else set(indexed))
		if invalid:
			raise BaseEmapiError(400, f"Following filters are not accepted for resource: {list(invalid)}")

	async def format_resources(self, resources: Iterable[EmapiDbModel], recursive: Optional[bool] = False) -> List[dict]:
		return [await self.format_resource(resource, recursive=recursive) for resource in resources]

	async def format_resource(self, resource: Union[EmapiDbModel, dict], recursive: Optional[bool] = False) -> dict:
		if isinstance(resource, dict):
			return resource
		out = self.format_model(resource)
		rels = await self.get_model_relationships(resource, recursive=recursive)
		if rels:
			out["relationships"] = rels
		return out


class ModelEndpoint(ApiEndpoint):
	async def get_instance(self, data: dict, raise_not_found: bool = False) -> EmapiDbModel:
		instance = await self.obj.get_or_none(id=data["id"])
		if not instance and raise_not_found:
			raise ModelNotFound
		return instance or self.obj.from_jsonapi(data)


class EventEndpoint(ApiEndpoint):
	def format_event_outcomes(self, event: Event) -> List[dict]:
		ret = []
		for out in event.outcomes:
			if isinstance(out, EmapiDbModel):
				out = self.format_model(out)
			elif isinstance(out, Outcome):
				out = self.format_outcome(out)
			ret.append(out)
		return ret


class MultiEndpoint:
	pass


class SingleEndpoint:
	pass


class SingleModelEndpoint(ModelEndpoint, SingleEndpoint):
	async def get(self, request: Request) -> Response:
		"""Returns a single resource"""
		res = await self.obj.get_or_none(**request.path_params)
		return JsonResponse({"data": await self.format_resource(res)})

	async def post(self, request: Request) -> Response:
		data = await self.get_json(request, ignore_erros=False)
		instance = self.obj.from_jsonapi(data)
		await instance.save()
		return JsonResponse({"data": self.format_model(instance)})

	async def put(self, request: Request) -> Response:
		data = await self.get_json(request, ignore_erros=False)
		instance = await self.get_instance(data)
		instance.update_from_dict(data["attributes"])
		await instance.save()
		return JsonResponse({"data": self.format_model(instance)})

	async def patch(self, request: Request) -> Response:
		data = await self.get_json(request, ignore_erros=False)
		instance = await self.get_instance(data, raise_not_found=True)
		instance.update_from_dict(data["attributes"])
		await instance.save()
		return JsonResponse({"data": self.format_model(instance)})

	async def delete(self, request: Request) -> Response:
		data = await self.get_json(request, ignore_erros=False)
		instance = await self.get_instance(data, raise_not_found=True)
		await instance.delete()
		return Response(status_code=204)


class MultiModelEndpoint(ModelEndpoint, MultiEndpoint):
	async def get(self, request: Request) -> Response:
		query = self.read_jsonapi_query(request)
		self.match_query_object(query)
		resources = await self.obj.filter(**query)
		return JsonResponse({"data": await self.format_resources(resources)})

	async def post(self, request: Request) -> Response:
		data = await self.get_json(request, ignore_erros=False)
		resources = list(map(self.obj.from_jsonapi, data["data"]))
		try:
			await self.obj.bulk_create(resources)
		except IntegrityError as ex:
			raise ModelConflict(409, detail=str(ex))
		return JsonResponse({"data": [self.format_model(r) for r in resources]})

	async def put(self, request: Request) -> Response:
		return JsonResponse({"status": "OK"})

	async def patch(self, request: Request) -> Response:
		data = await self.get_json(request, ignore_erros=False)
		ids = []
		res = {}
		for el in data["data"]:
			ids.append(el["id"])
			res[el["id"]] = el

		resources = await self.obj.filter(**{f"{self.obj._meta.pk_attr}__in": ids}).all()
		for instance in resources:
			instance.update_from_dict(res[getattr(instance, self.obj._meta.pk_attr)])

		await self.obj.bulk_update(resources, fields=self.obj._meta.fields_map.keys(), batch_size=100)

		return JsonResponse({"data": [self.format_model(r) for r in resources]})

	async def delete(self, request: Request) -> Response:
		data = await self.get_json(request, ignore_erros=False)
		self.obj.filter(**{f"{self.obj_meta_meta.pk_attr}__in": map(itemgetter("id"), data["data"])}).delete()
		return Response(status_code=204)


class SingleEventEndpoint(EventEndpoint, SingleEndpoint):
	async def post(self, request: Request) -> JsonResponse:
		data = await self.get_json(request, ignore_erros=True)
		if data:
			data = data["data"]["attributes"]
		data.update(request.path_params)
		event = self.obj()
		await event.do(request, **data)
		return JsonResponse({"data": self.format_event_outcomes(event)})

	async def delete(self, request: Request) -> Response:
		data = await self.get_json(request, ignore_erros=True)
		if data:
			data = data["data"]["attributes"]
		data.update(request.path_params)
		event = self.obj()
		await event.do(request, **data)
		return Response(status_code=204)


class MultiEventEndpoint(EventEndpoint, MultiEndpoint):
	async def post(self, request: Request) -> Response:
		data = await request.json()
		ret = []
		for el in data["data"]:
			event = self.obj()
			await event.do(request, **el["attributes"])
			ret.extend(self.format_event_outcomes(event))
		return JsonResponse({"data": ret})
