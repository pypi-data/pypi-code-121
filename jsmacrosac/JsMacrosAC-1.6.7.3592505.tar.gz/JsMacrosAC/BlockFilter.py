from typing import overload
from typing import List
from .ClassWrapperFilter import ClassWrapperFilter


class BlockFilter(ClassWrapperFilter):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self, methodName: str, methodArgs: List[object], filterArgs: List[object]) -> None:
		pass

	pass


