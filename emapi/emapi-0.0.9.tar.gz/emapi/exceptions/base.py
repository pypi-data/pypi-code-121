from starlette.exceptions import HTTPException


class BaseEmapiError(HTTPException):
	pass


class FormattedError:
	message_template = ""

	def __init__(self, **kwargs):
		super().__init__(self.message_template.format(**kwargs))
