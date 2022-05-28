class Metadata:
	def __init__(self, **kwargs):
		self._dictionary = {
			key:value for key, value in kwargs.items()
			if value is not None and value != '' and value != {} and value != []
		}

	def copy(self):
		return Metadata(**self._dictionary)

	def __getstate__(self):
		return self._dictionary

	def __setstate__(self, state):
		self._dictionary = state

	def __getitem__(self, item):
		if item in self._dictionary:
			return self._dictionary[item]
		else:
			return None

	def __setitem__(self, key, value):
		self._dictionary[key] = value

	def __contains__(self, item):
		return item in self._dictionary

	def update(self, x, inplace=False):
		"""
		:type x: dict or Metadata
		:rtype: Metadata
		"""
		if isinstance(x, Metadata):
			x = x._dictionary
		if inplace:
			metadata = self
		else:
			metadata = self.copy()

		metadata._dictionary.update({
			key: value for key, value in x.items() if value is not None and value != '' and value != {} and value != []
		})
		return metadata

	def __repr__(self):
		return repr(self._dictionary)

	def __str__(self):
		return str(self._dictionary)