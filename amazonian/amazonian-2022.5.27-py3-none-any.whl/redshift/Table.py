from .Column import Column
from .Metadata import Metadata
import warnings


class Table:
	def __init__(self, name, schema, echo=None):
		"""
		:type name: str
		:type schema: Schema
		:type echo: int or NoneType
		"""
		self._name = name
		self._schema = schema
		self._data = None
		self._columns_info = None
		self._columns = None
		self._dictionary = None
		self._metadata = None
		if name not in schema.table_names:
			raise KeyError(f'"{name}" not in "{schema}"')
		if echo is None:
			self._echo = max(0, self.schema.echo-1)
		else:
			self._echo = echo

	def __getstate__(self):
		return {
			'name': self.name,
			'columns_info': self.column_info,
			'columns': self._columns,
			'dictionary': self.dictionary,
			'metadata': self._metadata,
			'echo': self._echo
		}

	def __setstate__(self, state):
		self._name = state['name']
		self._schema = None
		self._columns_info = state['columns_info']
		self._columns = state['columns']
		self._dictionary = state['dictionary']
		self._metadata = state['metadata']
		self._echo = state['echo']
		self._data = None
		self.add_table_to_columns()

	def reset(self):
		self._data = None
		self._columns_info = None
		if self._columns is not None:
			for column in self.columns:
				column.reset()
		self._dictionary = None

	def __eq__(self, other):
		"""
		:type other: Table
		:rtype: bool
		"""
		return self.column_names == other.column_names

	def __ne__(self, other):
		return not self.__eq__(other=other)

	def __sub__(self, other):
		"""
		:type other: Table
		:rtype:
		"""
		if not isinstance(other, self.__class__):
			raise TypeError(f'{self} is of type {type(self)} but {other} is of type {type(other)}!')
		if self.schema != other.schema:
			warnings.warn(
				f'The two tables belong to different schemas: "{self.schema}" and "{other.schema}" respectively!'
			)
		if self.name != other.name:
			warnings.warn(
				f'The two tables have different names: "{self.name}" and "{other.name}" respectively!'
			)
		return {
			'num_rows_difference': self.num_rows - other.num_rows,
			'missing_column_names': [x for x in other.column_names if x not in self.column_names],
			'new_column_names': [x for x in self.column_names if x not in other.column_names]
		}

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
		return self.schema.metadata.update(self.metadata, inplace=False)

	def add_metadata(self, metadata, column=None):
		"""
		:type metadata: dict or Metadata
		:param str column: name of column
		"""
		if column is None:
			self.metadata = metadata
		else:
			self.column[column].metadata = metadata

	@property
	def echo(self):
		return self._echo is not None and self._echo

	@echo.setter
	def echo(self, echo):
		self._echo = echo

	@property
	def schema(self):
		return self._schema

	@property
	def name(self):
		return self._name

	@property
	def data(self):
		if self._data is None:
			query = 'SELECT * FROM ' + self.schema.name + '.' + self.name
			self._data = self.schema.database.get_dataframe(query=query, echo=self.echo)
		return self._data

	def get_head(self, num_rows=5):
		query = f'SELECT TOP {num_rows} * FROM ' + self.schema.name + '.' + self.name
		return self.schema.database.get_dataframe(query=query, echo=self.echo)

	@property
	def column_info(self):
		if self._columns_info is None:
			columns_data = self.schema.database.column_data
			self._columns_info = columns_data[
				(columns_data['schema'] == self.schema.name) & (columns_data['table'] == self.name)
			].copy().reset_index(drop=True)
		return self._columns_info

	@property
	def column_names(self):
		"""
		:rtype: list of str
		"""
		return list(self.column_info['column'].values)

	@property
	def column(self):
		"""
		:rtype: dict[str,Column]
		"""
		if self._columns is None:
			self._columns = {column_name: Column(name=column_name, table=self) for column_name in self.column_names}
		return self._columns.copy()

	@property
	def columns(self):
		"""
		:rtype: list[Column]
		"""
		return [column for column in self.column.values()]

	def add_table_to_columns(self):
		if self._columns is not None:
			for column in self.columns:
				column._table = self

	@property
	def shape(self):
		database_shape = self.schema.database.shape
		return database_shape[(database_shape['table'] == self.name) & (database_shape['schema'] == self.schema.name)]

	@property
	def dictionary(self):
		"""
		:rtype: dict
		"""
		if self._dictionary is None:
			self._dictionary = self.shape.iloc[0].to_dict()
		return self._dictionary.copy()

	@property
	def num_rows(self):
		return self.dictionary['num_rows']

	@property
	def num_columns(self):
		return self.dictionary['num_columns']

	def __str__(self):
		return f'{str(self.schema)}.{self.name}'

	def __repr__(self):
		return str(self)

	def __getitem__(self, item):
		try:
			return self.column[item]
		except KeyError:
			result = self.all_metadata[item]
			if result is None:
				raise AttributeError(f"table '{self.name}' has no attribute, column, or metadata '{item}'")
			else:
				return result

	def __getattr__(self, item):
		return self[item]
