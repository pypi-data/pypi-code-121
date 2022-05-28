class S3File:
	def __init__(self, dictionary):
		"""
		:type dictionary: dict or S3File
		"""
		if type(dictionary) is S3File:
			self._dict = dictionary._dict
		else:
			for important_key in ['Key', 'LastModified', 'Size', 'ETag']:
				if important_key not in dictionary: raise KeyError(f'missing {important_key} in dictionary!')
			self._dict = dictionary

	KEY_CONVERSION = {
		'path': 'Key',
		'modified_at': 'LastModified',
		'size': 'Size',
		'etag': 'ETag'
	}

	def get(self, key):
		return self._dict[self.KEY_CONVERSION[key]]

	@property
	def path(self):
		return self.get('path')

	@property
	def modified_at(self):
		return self.get('modified_at')

	@property
	def size(self):
		return self.get('size')

	def __repr__(self):
		return f'"{self.path}"  {self.size}  {self.modified_at}'


class S3Files:
	def __init__(self, file_list):
		"""
		:type file_list: list of S3File
		"""
		self._list = [S3File(each_file) for each_file in file_list]

	@property
	def list(self):
		return self._list

	def sort(self, by='path', reverse=True):
		"""
		:param by: 'path', 'modeified_at', 'size', 'etag'
		:param reverse:
		:return:
		"""
		if by is not None:
			self._list.sort(key=lambda x:x._dict[S3File.KEY_CONVERSION[by]], reverse=reverse)

	def __repr__(self):
		return '\n'.join([x.__repr__() for x in self._list])
