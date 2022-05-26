from typing import overload
from typing import TypeVar
from typing import Generic
from .IFilter import IFilter

T = TypeVar("T")

class IAdvancedFilter(IFilter, Generic[T]):
	"""
	Since: 1.6.5 
	"""

	@overload
	def and_(self, filter: IFilter) -> "IAdvancedFilter":
		pass

	@overload
	def or_(self, filter: IFilter) -> "IAdvancedFilter":
		pass

	@overload
	def xor(self, filter: IFilter) -> "IAdvancedFilter":
		pass

	@overload
	def not_(self) -> "IAdvancedFilter":
		pass

	pass


