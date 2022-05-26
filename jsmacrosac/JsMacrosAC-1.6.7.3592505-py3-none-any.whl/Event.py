from typing import overload


class Event:

	@overload
	def value(self) -> str:
		pass

	@overload
	def oldName(self) -> str:
		pass

	pass


