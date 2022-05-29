from .base import BaseEmapiError


class ModelConflict(BaseEmapiError):
	"""Duplicate key in INSERT/UPDATE operation"""

	status_code = 409


class ModelNotFound(BaseEmapiError):
	"""Instance not found with the given key"""

	status_code = 404
