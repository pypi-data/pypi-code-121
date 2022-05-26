import os


# Env variable class
class ConfigVariable():
	_name = None

	_value = None

	def __init__(self, key: str = '', default=None):
		self._name = key
		self._value = os.environ.get(key=key, default=default)

	def __str__(self):
		return str(self.__dict__)

	def val(self, default: str = ''):
		return default if self._value is None else self._value

	def int(self, default: int = 0):
		return default if self._value is None else int(self._value)

	def bool(self, default: bool = False):
		if self._value is not None:
			return (int(self._value) == 1) if self._value.isnumeric() \
				else self._value.lower() in ['yes', 'true', '1']
		else:
			return default

	def list(self, sep=' ', default: list = list):
		return default if self._value is None else self._value.split(sep=sep)

	def path(self, default='', joinpath: str = None):
		if joinpath is not None:
			return os.path.join(joinpath, self.val(default=default))
		return self.val(default=default)