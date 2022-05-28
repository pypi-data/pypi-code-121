from .Metadata import Metadata


class Column:
	def __init__(self, name, table, echo=None):
		self._name = name
		self._table = table
		self._value_counts = None
		if echo is None:
			self._echo = self.table.echo
		else:
			self._echo = echo
		self._metadata = None

	def reset(self):
		self._value_counts = None

	@property
	def name(self):
		return self._name

	@property
	def metadata(self):
		"""
		:rtype: Metadata
		"""
		return self._metadata

	@metadata.setter
	def metadata(self, metadata):
		"""
		:type metadata: dict or Metadata
		"""
		if self._metadata is None:
			if not isinstance(metadata, Metadata):
				metadata = Metadata(**metadata)
			self._metadata = metadata
		else:
			self._metadata.update(metadata, inplace=True)

	@property
	def all_metadata(self):
		"""
		:rtype: Metadata
		"""
		return self.table.all_metadata.update(self.metadata, inplace=False)

	@property
	def echo(self):
		return self._echo is not None and self._echo

	@echo.setter
	def echo(self, echo):
		self._echo = echo

	@property
	def table(self):
		return self._table

	@property
	def value_counts(self):
		"""
		:rtype: DataFrame
		"""
		if self._value_counts is None:
			self._value_counts = self.table.schema.database.get_dataframe(
				echo=self.echo,
				query=(
					f'SELECT \'{self.table.schema.name}\' AS "schema", \'{self.table.name}\' AS "table", '
					f'\'{self.name}\' AS "column", "{self.name}" AS "value", ' 
					f'COUNT(*) AS "count" FROM {self.table.schema.name}.{self.table.name} ' 
					f'GROUP BY "{self.name}" ORDER BY "count" DESC '
				)
			)
		return self._value_counts

	@property
	def unique_values(self):
		"""
		:rtype: list
		"""
		return list(self.value_counts['value'].values)

	def __str__(self):
		return f'"{self.name}" column'

	def __repr__(self):
		return str(self)

	def __getitem__(self, item):
		result = self.all_metadata[item]
		if result is None:
			raise AttributeError(f"column '{self.name}' has no attribute or metadata '{item}'")
		else:
			return result

	def __getattr__(self, item):
		return self[item]
