from typing import overload
from typing import TypeVar
from .ScriptTrigger import ScriptTrigger

Comparator = TypeVar["java.util.Comparator_xyz.wagyourtail.jsmacros.core.config.ScriptTrigger_"]

class Sorting_SortByTriggerName(Comparator):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def compare(self, a: ScriptTrigger, b: ScriptTrigger) -> int:
		pass

	pass


