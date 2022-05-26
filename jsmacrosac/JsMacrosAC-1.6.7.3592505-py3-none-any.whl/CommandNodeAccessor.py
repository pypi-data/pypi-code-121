from typing import overload
from typing import TypeVar

CommandNode = TypeVar["com.mojang.brigadier.tree.CommandNode_S_"]

class CommandNodeAccessor:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def remove(self, parent: CommandNode, name: str) -> CommandNode:
		pass

	pass


