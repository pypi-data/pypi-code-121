from typing import overload
from typing import TypeVar
from typing import Generic
from .MultiElementContainer import MultiElementContainer
from .AbstractSettingContainer import AbstractSettingContainer
from .SettingsOverlay_SettingField import SettingsOverlay_SettingField

T = TypeVar("T")
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class AbstractSettingField(Generic[T], MultiElementContainer):

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, parent: AbstractSettingContainer, field: SettingsOverlay_SettingField) -> None:
		pass

	pass


