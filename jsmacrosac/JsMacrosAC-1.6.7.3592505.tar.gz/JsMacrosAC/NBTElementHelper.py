from typing import overload
from typing import TypeVar
from typing import Generic
from .BaseHelper import BaseHelper
from .NBTElementHelper_NBTNumberHelper import NBTElementHelper_NBTNumberHelper
from .NBTElementHelper_NBTListHelper import NBTElementHelper_NBTListHelper
from .NBTElementHelper_NBTCompoundHelper import NBTElementHelper_NBTCompoundHelper

T = TypeVar("T")
NbtElement = TypeVar["net.minecraft.nbt.NbtElement"]

class NBTElementHelper(Generic[T], BaseHelper):
	"""
	Since: 1.5.1 
	"""

	@overload
	def getType(self) -> int:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def isNull(self) -> bool:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def isNumber(self) -> bool:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def isString(self) -> bool:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def isList(self) -> bool:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def isCompound(self) -> bool:
		"""
		Since: 1.5.1 
		"""
		pass

	@overload
	def asString(self) -> str:
		"""if element is a string, returns value.
otherwise returns toString representation.\n
		Since: 1.5.1 
		"""
		pass

	@overload
	def asNumberHelper(self) -> NBTElementHelper_NBTNumberHelper:
		"""check with NBTElementHelper#isNumber() first\n
		Since: 1.5.1 
		"""
		pass

	@overload
	def asListHelper(self) -> NBTElementHelper_NBTListHelper:
		"""check with NBTElementHelper#isList() first\n
		Since: 1.5.1 
		"""
		pass

	@overload
	def asCompoundHelper(self) -> NBTElementHelper_NBTCompoundHelper:
		"""check with NBTElementHelper#isCompound() first\n
		Since: 1.5.1 
		"""
		pass

	@overload
	def toString(self) -> str:
		pass

	@overload
	def resolve(self, element: NbtElement) -> "NBTElementHelper":
		"""
		Since: 1.5.1 
		"""
		pass

	pass


