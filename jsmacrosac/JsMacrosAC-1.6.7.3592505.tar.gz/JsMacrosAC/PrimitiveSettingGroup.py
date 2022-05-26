from typing import overload
from typing import List
from typing import TypeVar
from .AbstractSettingContainer import AbstractSettingContainer
from .SettingsOverlay import SettingsOverlay
from .SettingsOverlay_SettingField import SettingsOverlay_SettingField

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class PrimitiveSettingGroup(AbstractSettingContainer):

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, parent: SettingsOverlay, group: List[str]) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def onScrollbar(self, page: float) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def addSetting(self, setting: SettingsOverlay_SettingField) -> None:
		pass

	pass


