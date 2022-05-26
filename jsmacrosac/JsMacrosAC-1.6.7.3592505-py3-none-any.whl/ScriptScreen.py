from typing import overload
from typing import TypeVar
from .BaseScreen import BaseScreen
from .IScreen import IScreen
from .MethodWrapper import MethodWrapper

MatrixStack = TypeVar["net.minecraft.client.util.math.MatrixStack"]

class ScriptScreen(BaseScreen):
	"""just go look at IScreen since all the methods are done through a mixin...\n
	Since: 1.0.5 
	"""

	@overload
	def __init__(self, title: str, dirt: bool) -> None:
		pass

	@overload
	def setParent(self, parent: IScreen) -> None:
		"""
		Since: 1.4.0 

		Args:
			parent: parent screen to go to when this one exits. 
		"""
		pass

	@overload
	def setOnRender(self, onRender: MethodWrapper) -> None:
		"""add custom stuff to the render function on the main thread.\n
		Since: 1.4.0 

		Args:
			onRender: pos3d elements are mousex, mousey, tickDelta 
		"""
		pass

	@overload
	def render(self, matrices: MatrixStack, mouseX: int, mouseY: int, delta: float) -> None:
		pass

	@overload
	def close(self) -> None:
		pass

	pass


