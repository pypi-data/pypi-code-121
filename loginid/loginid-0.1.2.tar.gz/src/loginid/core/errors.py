from typing import Tuple, Union, Dict
class LoginIDError(Exception):
	"""Base class for exceptions in this module."""
	def __init__(self, status_code:int, error_code: str, message: str):
		self.status_code = status_code
		self.error_code = error_code
		self.message = message

		super().__init__(self.message)

	def __str__(self):
		return f"HTTP status code: {self.status_code}, error code: {self.error_code}, error message: {self.message}"