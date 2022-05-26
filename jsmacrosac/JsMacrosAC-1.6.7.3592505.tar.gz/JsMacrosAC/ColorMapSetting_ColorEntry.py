from typing import overload
from typing import List
from typing import TypeVar
from .AbstractMapSettingContainer_MapSettingEntry import AbstractMapSettingContainer_MapSettingEntry
from .ColorMapSetting import ColorMapSetting

TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class ColorMapSetting_ColorEntry(AbstractMapSettingContainer_MapSettingEntry):

	@overload
	def __init__(self, x: int, y: int, width: int, textRenderer: TextRenderer, parent: ColorMapSetting, key: str, value: List[float]) -> None:
		pass

	@overload
	def convertColorToString(self, color: List[float]) -> str:
		pass

	@overload
	def convertStringToColor(self, color: str) -> List[float]:
		pass

	@overload
	def convertColorToInt(self, color: List[float]) -> int:
		pass

	@overload
	def init(self) -> None:
		pass

	pass


