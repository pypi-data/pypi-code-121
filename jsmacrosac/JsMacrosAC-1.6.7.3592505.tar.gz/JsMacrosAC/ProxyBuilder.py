from typing import overload
from typing import List
from typing import TypeVar
from typing import Mapping
from typing import Generic
from .ProxyBuilder_MethodSigParts import ProxyBuilder_MethodSigParts
from .MethodWrapper import MethodWrapper

T = TypeVar("T")

class ProxyBuilder(Generic[T]):
	"""
	Since: 1.6.0 
	"""
	factory: ProxyFactory
	proxiedMethods: Mapping[ProxyBuilder_MethodSigParts, MethodWrapper]
	proxiedMethodDefaults: Mapping[str, MethodWrapper]

	@overload
	def __init__(self, clazz: Class, interfaces: List[Class]) -> None:
		pass

	@overload
	def addMethod(self, methodNameOrSig: str, proxyMethod: MethodWrapper) -> "ProxyBuilder":
		"""
		Since: 1.6.0 

		Args:
			proxyMethod: 
			methodNameOrSig: name of method or sig (the usual format) 

		Returns:
			self for chaining 
		"""
		pass

	@overload
	def buildInstance(self, constructorArgs: List[object]) -> T:
		"""
		Since: 1.6.0 

		Args:
			constructorArgs: args for the super constructor 

		Returns:
			new instance of the constructor 
		"""
		pass

	@overload
	def buildInstance(self, constructorSig: str, constructorArgs: List[object]) -> T:
		"""
		Since: 1.6.0 

		Args:
			constructorArgs: args for the super constructor 
			constructorSig: string signature (you can skip the init part) 

		Returns:
			new instance of the constructor 
		"""
		pass

	@overload
	def buildInstance(self, constructorSig: List[Class], constructorArgs: List[object]) -> T:
		"""
		Since: 1.6.0 

		Args:
			constructorArgs: args for the super constructor 
			constructorSig: string signature (you can skip the init part) 

		Returns:
			new instance of the constructor 
		"""
		pass

	pass


