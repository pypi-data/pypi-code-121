from typing import overload
from typing import TypeVar
from .MultiElementContainer import MultiElementContainer
from .ServiceScreen import ServiceScreen
from .ServiceTrigger import ServiceTrigger

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]
File = TypeVar["java.io.File"]
TextRenderer = TypeVar["net.minecraft.client.font.TextRenderer"]

class ServiceContainer(MultiElementContainer):
	service: str

	@overload
	def __init__(self, x: int, y: int, width: int, height: int, textRenderer: TextRenderer, parent: ServiceScreen, service: str) -> None:
		pass

	@overload
	def init(self) -> None:
		pass

	@overload
	def getEnabled(self) -> bool:
		pass

	@overload
	def getRunning(self) -> bool:
		pass

	@overload
	def getTrigger(self) -> ServiceTrigger:
		pass

	@overload
	def setFile(self, file: File) -> None:
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	pass


