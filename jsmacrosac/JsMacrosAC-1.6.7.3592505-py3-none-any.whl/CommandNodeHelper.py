from typing import overload
from typing import TypeVar
from .BaseHelper import BaseHelper

CommandNode = TypeVar["com.mojang.brigadier.tree.CommandNode"]

class CommandNodeHelper(BaseHelper):
	fabric: CommandNode

	@overload
	def __init__(self, base: CommandNode, fabric: CommandNode) -> None:
		pass

	pass


