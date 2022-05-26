from typing import overload
from typing import Mapping
from .BaseLibrary import BaseLibrary
from .HTTPRequest import HTTPRequest
from .HTTPRequest_Response import HTTPRequest_Response
from .Websocket import Websocket


class FRequest(BaseLibrary):
	"""Functions for getting and using raw java classes, methods and functions.

An instance of this class is passed to scripts as the 'Request' variable.\n
	Since: 1.1.8 
	"""

	@overload
	def __init__(self) -> None:
		pass

	@overload
	def create(self, url: str) -> HTTPRequest:
		"""create a HTTPRequest handler to the specified URL\n
		Since: 1.1.8 

		Args:
			url: 

		Returns:
			Request Wrapper 
		"""
		pass

	@overload
	def get(self, url: str) -> HTTPRequest_Response:
		"""
		Since: 1.1.8 

		Args:
			url: 
		"""
		pass

	@overload
	def get(self, url: str, headers: Mapping[str, str]) -> HTTPRequest_Response:
		"""send a GET request to the specified URL.\n
		Since: 1.1.8 

		Args:
			headers: 
			url: 

		Returns:
			Response Data 
		"""
		pass

	@overload
	def post(self, url: str, data: str) -> HTTPRequest_Response:
		"""
		Since: 1.1.8 

		Args:
			data: 
			url: 
		"""
		pass

	@overload
	def post(self, url: str, data: str, headers: Mapping[str, str]) -> HTTPRequest_Response:
		"""send a POST request to the specified URL.\n
		Since: 1.1.8 

		Args:
			headers: 
			data: 
			url: 

		Returns:
			Response Data 
		"""
		pass

	@overload
	def createWS(self, url: str) -> Websocket:
		"""Create a Websocket handler.\n
		Since: 1.2.7 

		Args:
			url: 
		"""
		pass

	@overload
	def createWS2(self, url: str) -> Websocket:
		"""Create a Websocket handler.\n
		Since: 1.1.9 

		Args:
			url: 
		"""
		pass

	pass


