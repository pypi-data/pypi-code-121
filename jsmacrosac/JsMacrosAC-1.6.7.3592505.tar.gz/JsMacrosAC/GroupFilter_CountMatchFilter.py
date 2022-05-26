from typing import overload
from typing import TypeVar
from typing import Generic
from .GroupFilter import GroupFilter

T = TypeVar("T")

class GroupFilter_CountMatchFilter(Generic[T], GroupFilter):

	@overload
	def __init__(self, operation: str, compareTo: float) -> None:
		pass

	@overload
	def apply(self, t: T) -> bool:
		pass

	pass


