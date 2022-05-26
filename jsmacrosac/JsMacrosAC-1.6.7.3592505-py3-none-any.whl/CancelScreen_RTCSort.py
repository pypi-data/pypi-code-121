from typing import overload
from typing import TypeVar
from .RunningContextContainer import RunningContextContainer

Comparator = TypeVar["java.util.Comparator_xyz.wagyourtail.jsmacros.client.gui.containers.RunningContextContainer_"]

class CancelScreen_RTCSort(Comparator):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def compare(self, arg0: RunningContextContainer, arg1: RunningContextContainer) -> int:
		pass

	pass


