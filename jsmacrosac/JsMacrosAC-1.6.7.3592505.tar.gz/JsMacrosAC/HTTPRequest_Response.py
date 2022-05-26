from typing import overload
from typing import List
from typing import TypeVar
from typing import Mapping

InputStream = TypeVar["java.io.InputStream"]

class HTTPRequest_Response:
	"""
	Since: 1.1.8 
	"""
	headers: Mapping[str, List[str]]
	responseCode: int

	@overload
	def __init__(self, inputStream: InputStream, responseCode: int, headers: Mapping[str, List[str]]) -> None:
		pass

	@overload
	def text(self) -> str:
		"""
		Since: 1.1.8 
		"""
		pass

	@overload
	def json(self) -> object:
		"""Don't use this. Parse HTTPRequest_Response#text() in the guest language\n
		Since: 1.1.8 
		"""
		pass

	@overload
	def byteArray(self) -> List[float]:
		"""
		Since: 1.2.2 
		"""
		pass

	pass


