from typing import overload
from typing import TypeVar

ClickEvent = TypeVar["net.minecraft.text.ClickEvent"]
Runnable = TypeVar["java.lang.Runnable"]

class CustomClickEvent(ClickEvent):

	@overload
	def __init__(self, event: Runnable) -> None:
		pass

	@overload
	def hashCode(self) -> int:
		pass

	@overload
	def getEvent(self) -> Runnable:
		pass

	pass


