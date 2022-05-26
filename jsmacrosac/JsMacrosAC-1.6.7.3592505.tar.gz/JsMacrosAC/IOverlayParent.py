from typing import overload
from typing import TypeVar
from .IContainerParent import IContainerParent
from .OverlayContainer import OverlayContainer

Element = TypeVar["net.minecraft.client.gui.Element"]

class IOverlayParent(IContainerParent):

	@overload
	def closeOverlay(self, overlay: OverlayContainer) -> None:
		pass

	@overload
	def setFocused(self, focused: Element) -> None:
		pass

	@overload
	def getChildOverlay(self) -> OverlayContainer:
		pass

	pass


