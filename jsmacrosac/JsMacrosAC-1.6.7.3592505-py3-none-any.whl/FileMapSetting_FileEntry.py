from typing import overload
from typing import TypeVar
from .AbstractMapSettingContainer_MapSettingEntry import AbstractMapSettingContainer_MapSettingEntry
from .FileMapSetting import FileMapSetting

TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class FileMapSetting_FileEntry(AbstractMapSettingContainer_MapSettingEntry):

	@overload
	def __init__(self, x: int, y: int, width: int, textRenderer: TextRenderer, parent: FileMapSetting, key: str, value: str) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	pass


