from typing import overload
from typing import TypeVar

ClickEvent_Action = TypeVar["net.minecraft.text.ClickEvent.Action"]

class MixinStyleSerializer:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def redirectClickGetAction(self, action: ClickEvent_Action) -> str:
		pass

	pass


