from typing import overload


class TickSync:
	"""
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def waitTick(self) -> None:
		pass

	@overload
	def tick(self) -> None:
		pass

	pass


