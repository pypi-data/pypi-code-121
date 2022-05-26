from typing import overload
from .ILoomScreen import ILoomScreen


class MixinLoomScreen(ILoomScreen):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def jsmacros_canApplyDyePattern(self) -> bool:
		pass

	pass


