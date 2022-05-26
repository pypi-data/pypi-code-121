from typing import overload
from typing import List
from typing import TypeVar
from typing import Mapping
from .ScriptTrigger import ScriptTrigger
from .ServiceTrigger import ServiceTrigger

JsonObject = TypeVar["com.google.gson.JsonObject"]

class CoreConfigV2:
	maxLockTime: float
	defaultProfile: str
	profiles: Mapping[str, List[ScriptTrigger]]
	services: Mapping[str, ServiceTrigger]
	extraJsOptions: Mapping[str, str]

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def getCurrentProfile(self) -> str:
		pass

	@overload
	def setCurrentProfile(self, pname: str) -> None:
		pass

	@overload
	def profileOptions(self) -> List[str]:
		pass

	@overload
	def fromV1(self, v1: JsonObject) -> None:
		pass

	pass


