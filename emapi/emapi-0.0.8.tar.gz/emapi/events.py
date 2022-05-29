from copy import deepcopy
from inspect import getdoc
from functools import cache
from typing import Optional, Any
from dataclasses import dataclass, fields, _MISSING_TYPE

from starlette.requests import Request

from .base import ApiMember
from .tools import get_method_signature_data, format_field


@dataclass
class Outcome:
	class Meta(ApiMember.Meta):
		abstract = True

	id: str  # Unique id of the outcome

	def dict(self) -> dict:
		return deepcopy(self.__dict__)

	@classmethod
	@cache
	def describe(cls) -> dict:
		return {
			"name": f"{cls.__module__}.{cls.__name__}",
			"type": "event",
			"description": getdoc(cls),
			"pk": format_field({"name": "id", "description": f"{cls.__name__} unique identifier", "field_type": "str"}),
			"properties": {
				field.name: format_field(
					{
						"name": field.name,
						"description": "",
						"default": field.default if not isinstance(field.default, _MISSING_TYPE) else "",
						"field_type": field.type,
					}
				)
				for field in fields(cls)
				if field.name != "id"
			},
		}


class Event(ApiMember):
	"""
	Event
	"""

	class Meta(ApiMember.Meta):
		multi = False
		base_model = None
		need_resource = True
		outcomes = tuple()
		methods = ("post",)

	def __init__(self, context: Optional[dict[Any, Any]] = None):
		self.context = context or {}
		self.outcomes = []

	async def do(self, request: Request, *args, **kwargs) -> Any:
		raise NotImplementedError

	@classmethod
	@cache
	def describe(cls) -> dict:
		return {
			"name": f"{cls.__module__}.{cls.__name__}",
			"type": "event",
			"description": getdoc(cls),
			"pk": cls.Meta.base_model.describe()["pk"],
			"properties": get_method_signature_data(cls.do),
		}
