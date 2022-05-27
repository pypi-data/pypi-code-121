class BaseFunction:
	"""

	Examples
	--------
	>>> BaseFunction("SomeFunction", "Text").res
	True or False
	"""

	def __init__(self, command: str, text: str):
		self.command = command.strip()
		self.text = text

		self.check_command()
		self.res = self.execute()

	def check_command(self):
		"""
		Checks command syntax

		Raises
		------
		Exception:
			Any exception from child classes.
		"""
		...

	def execute(self) -> bool:
		"""

		Returns
		-------
		bool
		"""
		...