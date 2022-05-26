from typing import overload
from typing import TypeVar
from typing import Mapping
from .Mappings_ClassData import Mappings_ClassData
from .Mappings_MappedClass import Mappings_MappedClass

T = TypeVar("T")

class Mappings:
	"""
	Since: 1.3.1 
	"""
	mappingsource: str

	@overload
	def __init__(self, mappingsource: str) -> None:
		pass

	@overload
	def getMappings(self) -> Mapping[str, Mappings_ClassData]:
		"""
		Since: 1.3.1 

		Returns:
			mappings from Intermediary to Named 
		"""
		pass

	@overload
	def getReversedMappings(self) -> Mapping[str, Mappings_ClassData]:
		"""
		Since: 1.3.1 

		Returns:
			mappings from Named to Intermediary 
		"""
		pass

	@overload
	def remapClass(self, instance: T) -> Mappings_MappedClass:
		"""
		Since: 1.6.0 
		"""
		pass

	@overload
	def getClass(self, className: str) -> Mappings_MappedClass:
		"""gets the class without instance, so can only access static methods/fields

		Args:
			className: 
		"""
		pass

	pass


