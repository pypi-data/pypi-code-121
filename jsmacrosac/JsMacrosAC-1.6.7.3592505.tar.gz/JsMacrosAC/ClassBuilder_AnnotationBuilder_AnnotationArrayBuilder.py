from typing import overload
from typing import TypeVar
from typing import Generic
from .ClassBuilder_AnnotationBuilder import ClassBuilder_AnnotationBuilder

U = TypeVar("U")

class ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder(Generic[U]):

	@overload
	def __init__(self, parent: U, constPool: ConstPool) -> None:
		pass

	@overload
	def putString(self, value: str) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putBoolean(self, value: bool) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putByte(self, value: float) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putChar(self, value: str) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putShort(self, value: float) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putInt(self, value: int) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putLong(self, value: float) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putFloat(self, value: float) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putDouble(self, value: float) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putClass(self, value: Class) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putEnum(self, value: ) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def putAnnotation(self, annotationClass: Class) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putArray(self, annotationClass: Class) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def finish(self) -> U:
		pass

	pass


