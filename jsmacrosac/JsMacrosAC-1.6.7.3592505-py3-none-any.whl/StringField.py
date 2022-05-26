from typing import overload
from typing import TypeVar
from .AbstractSettingField import AbstractSettingField
from .AbstractSettingContainer import AbstractSettingContainer
from .SettingsOverlay_SettingField import SettingsOverlay_SettingField

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class StringField(AbstractSettingField):

	@overload
	def __init__(self, x: int, y: int, width: int, textRenderer: TextRenderer, parent: AbstractSettingContainer, field: SettingsOverlay_SettingField) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def setPos(self, x: int, y: int, width: int, height: int) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


