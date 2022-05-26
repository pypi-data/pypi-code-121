from typing import overload
from typing import List


class Library:
	"""Base Function interface.
	"""

	@overload
	def value(self) -> str:
		pass

	@overload
	def languages(self) -> List[Class]:
		pass

	pass


