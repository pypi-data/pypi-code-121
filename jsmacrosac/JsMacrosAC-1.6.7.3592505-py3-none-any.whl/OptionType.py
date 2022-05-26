from typing import overload
from typing import List


class OptionType:

	@overload
	def value(self) -> str:
		pass

	@overload
	def options(self) -> List[str]:
		pass

	pass


