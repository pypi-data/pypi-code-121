from typing import overload
from typing import TypeVar
from typing import Mapping

T = TypeVar("T")
JsonObject = TypeVar["com.google.gson.JsonObject"]
Logger = TypeVar["org.apache.logging.log4j.Logger"]
File = TypeVar["java.io.File"]

class ConfigManager:
	optionClasses: Mapping[str, Class]
	options: Mapping[Class, object]
	configFolder: File
	macroFolder: File
	configFile: File
	LOGGER: Logger
	rawOptions: JsonObject

	@overload
	def __init__(self, configFolder: File, macroFolder: File, logger: Logger) -> None:
		pass

	@overload
	def reloadRawConfigFromFile(self) -> None:
		pass

	@overload
	def convertConfigFormat(self) -> None:
		pass

	@overload
	def convertConfigFormat(self, clazz: Class) -> None:
		pass

	@overload
	def getOptions(self, optionClass: Class) -> T:
		pass

	@overload
	def addOptions(self, key: str, optionClass: Class) -> None:
		pass

	@overload
	def loadConfig(self) -> None:
		pass

	@overload
	def loadDefaults(self) -> None:
		pass

	@overload
	def saveConfig(self) -> None:
		pass

	pass


