from typing import overload
from typing import TypeVar
from .AbstractMapSettingContainer_MapSettingEntry import AbstractMapSettingContainer_MapSettingEntry
from .StringMapSetting import StringMapSetting

TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class StringMapSetting_StringEntry(AbstractMapSettingContainer_MapSettingEntry):

	@overload
	def __init__(self, x: int, y: int, width: int, textRenderer: TextRenderer, parent: StringMapSetting, key: str, value: str) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	pass


