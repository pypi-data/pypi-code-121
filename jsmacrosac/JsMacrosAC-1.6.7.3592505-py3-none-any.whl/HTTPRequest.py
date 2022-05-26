from typing import overload
from typing import Mapping
from .HTTPRequest_Response import HTTPRequest_Response


class HTTPRequest:
	"""
	Since: 1.1.8 
	"""
	headers: Mapping[str, str]
	conn: URL

	@overload
	def __init__(self, url: str) -> None:
		pass

	@overload
	def addHeader(self, key: str, value: str) -> "HTTPRequest":
		"""
		Since: 1.1.8 

		Args:
			value: 
			key: 
		"""
		pass

	@overload
	def get(self) -> HTTPRequest_Response:
		"""
		Since: 1.1.8 
		"""
		pass

	@overload
	def post(self, data: str) -> HTTPRequest_Response:
		"""
		Since: 1.1.8 

		Args:
			data: 
		"""
		pass

	pass


