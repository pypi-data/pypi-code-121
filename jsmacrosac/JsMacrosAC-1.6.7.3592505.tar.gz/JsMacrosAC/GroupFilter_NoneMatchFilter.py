from typing import overload
from typing import TypeVar
from typing import Generic
from .GroupFilter import GroupFilter

T = TypeVar("T")

class GroupFilter_NoneMatchFilter(Generic[T], GroupFilter):

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def apply(self, t: T) -> bool:
		pass

	pass


