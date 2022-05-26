from typing import overload
from typing import List
from typing import TypeVar
from typing import Mapping
from typing import Generic
from .MethodWrapper import MethodWrapper
from .ClassBuilder_FieldBuilder import ClassBuilder_FieldBuilder
from .ClassBuilder_MethodBuilder import ClassBuilder_MethodBuilder
from .ClassBuilder_ConstructorBuilder import ClassBuilder_ConstructorBuilder
from .ClassBuilder_AnnotationBuilder import ClassBuilder_AnnotationBuilder

T = TypeVar("T")

class ClassBuilder(Generic[T]):
	"""
	Since: 1.6.5 
	"""
	methodWrappers: Mapping[str, MethodWrapper]
	ctClass: CtClass

	@overload
	def __init__(self, name: str, parent: Class, interfaces: List[Class]) -> None:
		pass

	@overload
	def addField(self, fieldType: Class, name: str) -> "ClassBuilder_FieldBuilder":
		pass

	@overload
	def addMethod(self, returnType: Class, name: str, params: List[Class]) -> "ClassBuilder_MethodBuilder":
		pass

	@overload
	def addConstructor(self, params: List[Class]) -> "ClassBuilder_ConstructorBuilder":
		pass

	@overload
	def addClinit(self) -> "ClassBuilder_ConstructorBuilder":
		pass

	@overload
	def addAnnotation(self, type: Class) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def finishBuildAndFreeze(self) -> Class:
		pass

	pass


