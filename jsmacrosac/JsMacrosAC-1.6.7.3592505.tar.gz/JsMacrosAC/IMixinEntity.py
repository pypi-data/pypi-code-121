from typing import overload


class IMixinEntity:

	@overload
	def jsmacros_setGlowingColor(self, glowingColor: int) -> None:
		pass

	@overload
	def jsmacros_resetColor(self) -> None:
		pass

	@overload
	def jsmacros_setForceGlowing(self, glowing: int) -> None:
		"""

		Args:
			glowing: 1 for enabled, 2 for forced 
		"""
		pass

	pass


