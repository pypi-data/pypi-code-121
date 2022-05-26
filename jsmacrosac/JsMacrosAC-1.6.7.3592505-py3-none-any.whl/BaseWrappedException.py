from typing import overload
from typing import TypeVar
from typing import Generic
from .BaseWrappedException_SourceLocation import BaseWrappedException_SourceLocation

T = TypeVar("T")
StackTraceElement = TypeVar["java.lang.StackTraceElement"]

class BaseWrappedException(Generic[T]):
	stackFrame: T
	location: BaseWrappedException_SourceLocation
	message: str
	next: "BaseWrappedException"

	@overload
	def __init__(self, exception: T, message: str, location: BaseWrappedException_SourceLocation, next: "BaseWrappedException") -> None:
		pass

	@overload
	def wrapHostElement(self, t: StackTraceElement, next: "BaseWrappedException") -> "BaseWrappedException":
		pass

	pass


