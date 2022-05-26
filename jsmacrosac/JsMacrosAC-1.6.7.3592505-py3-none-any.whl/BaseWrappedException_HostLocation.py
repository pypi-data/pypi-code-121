from typing import overload
from .BaseWrappedException_SourceLocation import BaseWrappedException_SourceLocation


class BaseWrappedException_HostLocation(BaseWrappedException_SourceLocation):
	location: str

	@overload
	def __init__(self, location: str) -> None:
		pass

	@overload
	def toString(self) -> str:
		pass

	pass


