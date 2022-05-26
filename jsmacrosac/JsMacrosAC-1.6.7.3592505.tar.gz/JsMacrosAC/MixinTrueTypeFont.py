from typing import overload


class MixinTrueTypeFont:

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def modifyWidth(self, w: int, i: int) -> int:
		pass

	@overload
	def modifyHeight(self, h: int, i: int) -> int:
		pass

	pass


