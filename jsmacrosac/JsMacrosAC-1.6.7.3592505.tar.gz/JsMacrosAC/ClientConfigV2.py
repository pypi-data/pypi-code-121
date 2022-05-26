from typing import overload
from typing import List
from typing import TypeVar
from typing import Mapping
from .Sorting_MacroSortMethod import Sorting_MacroSortMethod

JsonObject = TypeVar["com.google.gson.JsonObject"]
Comparator = TypeVar["java.util.Comparator_xyz.wagyourtail.jsmacros.core.config.ScriptTrigger_"]

class ClientConfigV2:
	sortMethod: Sorting_MacroSortMethod
	disableKeyWhenScreenOpen: bool
	editorTheme: Mapping[str, List[float]]
	editorLinterOverrides: Mapping[str, str]
	editorHistorySize: int
	editorSuggestions: bool
	editorFont: str
	externalEditor: bool
	externalEditorCommand: str

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def languages(self) -> List[str]:
		pass

	@overload
	def getFonts(self) -> List[str]:
		pass

	@overload
	def getThemeData(self) -> Mapping[str, List[float]]:
		pass

	@overload
	def getSortComparator(self) -> Comparator:
		pass

	@overload
	def fromV1(self, v1: JsonObject) -> None:
		pass

	pass


