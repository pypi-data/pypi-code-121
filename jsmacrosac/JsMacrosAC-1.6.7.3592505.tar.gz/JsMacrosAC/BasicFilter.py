from typing import overload
from typing import TypeVar
from typing import Generic
from .IAdvancedFilter import IAdvancedFilter
from .IFilter import IFilter

T = TypeVar("T")

class BasicFilter(IAdvancedFilter, Generic[T]):
	"""
	Since: 1.6.5 
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def and_(self, filter: IFilter) -> IAdvancedFilter:
		pass

	@overload
	def or_(self, filter: IFilter) -> IAdvancedFilter:
		pass

	@overload
	def xor(self, filter: IFilter) -> IAdvancedFilter:
		pass

	@overload
	def not_(self) -> IAdvancedFilter:
		pass

	pass


