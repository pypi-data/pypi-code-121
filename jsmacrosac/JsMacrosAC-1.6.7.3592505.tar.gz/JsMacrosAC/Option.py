from typing import overload
from typing import List
from .OptionType import OptionType


class Option:

	@overload
	def translationKey(self) -> str:
		pass

	@overload
	def group(self) -> List[str]:
		pass

	@overload
	def setter(self) -> str:
		pass

	@overload
	def getter(self) -> str:
		pass

	@overload
	def options(self) -> str:
		pass

	@overload
	def type(self) -> OptionType:
		pass

	pass


