from typing import overload
from typing import TypeVar
from typing import Generic
from .ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder import ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder

T = TypeVar("T")

class ClassBuilder_AnnotationBuilder(Generic[T]):

	@overload
	def putString(self, key: str, value: str) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putBoolean(self, key: str, value: bool) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putByte(self, key: str, value: float) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putChar(self, key: str, value: str) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putShort(self, key: str, value: float) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putInt(self, key: str, value: int) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putLong(self, key: str, value: float) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putFloat(self, key: str, value: float) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putDouble(self, key: str, value: float) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putClass(self, key: str, value: Class) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putEnum(self, key: str, value: ) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putAnnotation(self, key: str, annotationClass: Class) -> "ClassBuilder_AnnotationBuilder":
		pass

	@overload
	def putArray(self, key: str, annotationClass: Class) -> "ClassBuilder_AnnotationBuilder_AnnotationArrayBuilder":
		pass

	@overload
	def finish(self) -> T:
		pass

	pass


