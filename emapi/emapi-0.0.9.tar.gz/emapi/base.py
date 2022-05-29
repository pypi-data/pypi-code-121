from typing import Optional, Any, Iterable


class Settings:
	version = None
	ecosystem = None
	environment = None
	debug = None
	database_url = None
	app_name = None

	@classmethod
	def get(cls, key, default: Optional[Any] = None) -> Any:
		try:
			return getattr(cls, key)
		except AttributeError:
			if default is None:
				raise
			return default


class ApiMember:
	class Meta:
		version = 1
		abstract = False
		base_model = None
		multi = True
		api_excluded = False
		api_excluded_fields = tuple()
		need_resource = False

		methods = ("get", "post", "put", "patch", "delete")

	@classmethod
	def hierarchy(cls) -> Iterable["ApiMember"]:
		yield cls
		if cls.Meta.base_model:
			yield from cls.Meta.base_model.hierarchy()
