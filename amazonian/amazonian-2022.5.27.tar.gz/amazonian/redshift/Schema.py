from .Table import Table
from .Metadata import Metadata


class Schema:
	def __init__(self, name, database, echo=None):
		"""
		:type name: str
		:type database: .Redshift.Redshift
		:type echo: int or NoneType
		"""
		self._name = name
		self._database = database
		self._table_dict = None
		self._metadata = None
		if echo is None:
			self._echo = max(0, self.database.echo-1)
		else:
			self._echo = echo
		if name not in database.get_schema_list():
			raise KeyError('schema "{name}" not in database!')

	def reset(self):
		if self._table_dict is not None:
			for table in self.tables:
				table.reset()

	def __eq__(self, other):
		"""
		:type other: Schema
		:rtype: bool
		"""
		return self.table_names == other.table_names

	def __ne__(self, other):
		return not self.__eq__(other=other)

	def __getstate__(self):
		return {
			'name': self.name,
			'metadata': self._metadata,
			'tables': self._table_dict,
			'echo': self._echo
		}

	def __setstate__(self, state):
		self._name = state['name']
		self._database = None
		self._table_dict = state['tables']
		self._metadata = state['metadata']
		self._echo = state['echo']
		self.add_schema_to_tables()

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

	def add_metadata(self, metadata, table=None, column=None):
		"""
		:type metadata: dict or Metadata
		:param str table: name of table
		:param str column: name of column
		"""
		if table is None:
			self.metadata = metadata
		else:
			self.table[table].add_metadata(metadata=metadata, column=column)

	@property
	def echo(self):
		return self._echo is not None and self._echo

	@echo.setter
	def echo(self, echo):
		self._echo = echo

	@property
	def database(self):
		"""
		:rtype: .Redshift.Redshift
		"""
		return self._database

	@property
	def table_names(self):
		try:
			return self.database.hierarchy[self._name]
		except:
			return []

	# @property
	# def view_names(self):
	# 	try:
	# 		return self.database.hierarchy[self._name]#['views']
	# 	except:
	# 		return []

	@property
	def table(self):
		"""
		:rtype: dict[str,Table]
		"""
		if self._table_dict is None:
			self._table_dict = {name: Table(name=name, schema=self) for name in self.table_names}
		return self._table_dict

	@property
	def tables(self):
		"""
		:rtype: list[Table]
		"""
		return [table for table in self.table.values()]

	@property
	def columns(self):
		"""
		:rtype: list[Column]
		"""
		return [column for table in self.tables for column in table.columns]

	def add_schema_to_tables(self):
		if self.table is not None:
			for table in self.tables:
				table._schema = self
				table.add_table_to_columns()

	@property
	def name(self):
		return self._name

	@property
	def shape(self):
		return self.database.shape[self.database.shape['schema'] == self.name]

	def __str__(self):
		return f'{str(self.database)}.{self.name}'

	def __repr__(self):
		return str(self)

	def __getitem__(self, item):
		try:
			return self.table[item]
		except KeyError:
			result = self.metadata[item]
			if result is None:
				raise AttributeError(f"schema '{self.name}' has no attribute, table, or metadata '{item}'")
			else:
				return result

	def __getattr__(self, item):
		return self[item]
