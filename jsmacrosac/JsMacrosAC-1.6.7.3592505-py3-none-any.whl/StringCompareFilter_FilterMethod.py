from typing import overload
from typing import List
from .ICompare import ICompare


class StringCompareFilter_FilterMethod:
	CONTAINS: "StringCompareFilter_FilterMethod"
	EQUALS: "StringCompareFilter_FilterMethod"
	STARTS_WITH: "StringCompareFilter_FilterMethod"
	ENDS_WITH: "StringCompareFilter_FilterMethod"
	MATCHES: "StringCompareFilter_FilterMethod"

	@overload
	def values(self) -> List["StringCompareFilter_FilterMethod"]:
		pass

	@overload
	def valueOf(self, name: str) -> "StringCompareFilter_FilterMethod":
		pass

	@overload
	def getMethod(self) -> ICompare:
		pass

	pass


