from typing import Optional
from inspect import getdoc
from functools import cache

from tortoise import models, fields

from ..base import ApiMember
from ..tools import format_field


class EmapiDbModel(models.Model, ApiMember):
	"""
	Model
	"""

	class Meta(ApiMember.Meta):
		abstract = True

	@classmethod
	@property
	def pk_field(cls) -> dict:
		return cls.describe()["pk"]

	@classmethod
	@property
	def generated_id(cls) -> bool:
		pk_field = cls.describe()["pk"]
		return pk_field["generated"] or pk_field["default"]

	@classmethod
	@cache
	def describe(cls) -> dict:
		data = super().describe()
		ret = {
			"name": f"{cls.__module__}.{cls.__name__}",
			"description": getdoc(cls),
			"type": "model",
			"pk": format_field(data["pk_field"]),
			"properties": {},
			"filters": {},
			"relationships": {},
		}
		for f in data["data_fields"]:
			if f["name"] in cls.Meta.api_excluded_fields:
				continue
			api_field = format_field(f)
			ret["properties"][f["name"]] = api_field
			if f["indexed"]:
				ret["filters"][f["name"]] = api_field
		for f in cls._meta.fetch_fields:
			if cls._meta.fields_map[f].model != cls:
				rel_data = cls._meta.fields_map[f].model.describe()
			else:
				rel_data = ret
			ret["relationships"][f] = rel_data
		return ret

	async def get_relationships(self) -> dict:
		if not self._meta.fetch_fields:
			return {}
		await self.fetch_related(*self._meta.fetch_fields)
		out = {}
		for f in self._meta.fetch_fields:
			rel = getattr(self, f)
			if isinstance(rel, fields.ReverseRelation):
				for member in getattr(self, f) or []:
					out.setdefault(f, []).append(member)
			elif isinstance(rel, EmapiDbModel):
				out[f] = [rel]
		return out

	@classmethod
	def make_id(cls) -> None:
		return None

	def dict(self, for_api_response: Optional[bool] = False) -> dict:
		ret = {}
		for k, v in dict(self).items():
			if k in self._meta.m2m_fields:
				continue
			if for_api_response and k in self.Meta.api_excluded_fields:
				continue
			if isinstance(self._meta.fields_map[k], fields.UUIDField) and v:
				v = str(v)
			ret[k] = v
		return ret

	@classmethod
	def make(cls, data: dict) -> "EmapiDbModel":
		data.setdefault(cls._meta.pk_attr, cls.make_id)
		return cls(**{k: v for k, v in data.items() if k not in cls._meta.m2m_fields})

	@classmethod
	def from_jsonapi(cls, data: dict) -> "EmapiDbModel":
		if not cls.generated_id:
			data["attributes"][cls._meta.pk_attr] = data["id"]
		return cls.make(data["attributes"])

	def __str__(self):
		try:
			unique_key = "-".join(getattr(self, a) for a in self._meta.unique_together[0])
		except (AttributeError, IndexError):
			unique_key = ""
		model_id = f"{getattr(self, self._meta.pk_attr)} {unique_key}"
		return f"<{self.__class__.__name__} {model_id}>"
