from .BasicRedshift import BasicRedshift
from .Schema import Schema
from .Table import Table
from .Column import Column
from .Snapshot import Snapshot


class Redshift(BasicRedshift):
	def __init__(self, user_id, password, server, database, port='5439', echo=0):
		super().__init__(user_id=user_id, password=password, port=port, server=server, database=database)
		self._schema_dict = None
		self._hierarchy = None
		self._table_data = None
		self._column_data = None
		self._echo = echo

	def reset(self):
		if self._schema_dict is not None:
			for schema in self.schemas:
				schema.reset()
		self._hierarchy = None
		self._table_data = None
		self._column_data = None

	def __getstate__(self):
		state = super().__getstate__()
		state.update({
			'schemas': self._schema_dict,
			'hierarchy': self._hierarchy,
			'table_data': self._table_data,
			'column_data': self._column_data,
			'echo': self._echo,
		})
		return state

	def __setstate__(self, state):
		super().__setstate__(state)
		self._schema_dict = state['schemas']
		self._hierarchy = state['hierarchy']
		self._table_data = state['table_data']
		self._column_data = state['column_data']
		self._echo = state['echo']
		self.add_database_to_schemas()

	@property
	def echo(self):
		return self._echo is not None and self._echo

	@echo.setter
	def echo(self, echo):
		self._echo = echo

	def _update_tables_data(self):
		self._table_data = self.get_tables_data(echo=self.echo)

	@property
	def table_data(self):
		"""
		:rtype: DataFrame
		"""
		if self._table_data is None:
			self._update_tables_data()
		return self._table_data

	shape = table_data

	def _update_columns_data(self):
		self._column_data = self.get_columns_data(echo=self.echo)

	@property
	def column_data(self):
		"""
		:rtype: DataFrame
		"""
		if self._column_data is None:
			self._update_columns_data()
		return self._column_data

	def _update_hierarchy(self):
		self._hierarchy = {
			schema: list(data['table'].unique()) for schema, data in self.table_data.groupby(by='schema')
		}

	@property
	def hierarchy(self):
		"""
		:rtype: dict[str,list[str]]
		"""
		if self._hierarchy is None:
			self._update_hierarchy()
		return self._hierarchy

	def _update_schemas(self):
		self._schema_dict = {schema: Schema(name=schema, database=self) for schema in self.get_schema_list()}

	@property
	def schema(self):
		"""
		:rtype: dict[str,Schema]
		"""
		if self._schema_dict is None:
			self._update_schemas()
		return self._schema_dict

	@property
	def schemas(self):
		"""
		:rtype: list[Schema]
		"""
		return [schema for schema in self.schema.values()]

	@property
	def table_list(self):
		"""
		:rtype: list[Table]
		"""
		return [table for schema in self.schemas for table in schema.tables]

	@property
	def columns(self):
		"""
		:rtype: list[Column]
		"""
		return [column for table in self.table_list for column in table.columns]

	def add_database_to_schemas(self):
		if self._schema_dict is not None:
			for schema in self.schemas:
				schema._database = self
				schema.add_schema_to_tables()

	def get_schema_list(self):
		return list(self.table_data['schema'].unique())

	def get_table(self, schema, table):
		return self.schema[schema].table[table]

	def __getitem__(self, item):
		return self.schema[item]

	def __getattr__(self, item):
		return self[item]

	def refresh(self):
		self.reset()
		self._update_tables_data()
		self._update_columns_data()
		self._update_hierarchy()
		self._update_schemas()

	def take_snapshot(self):
		return Snapshot(database=self)

	def add_metadata(self, metadata, schema, table=None, column=None):
		"""
		:type metadata: dict or Metadata
		:param str schema: name of schema
		:param str table: name of table
		:param str column: name of column
		"""
		if table == '':
			table = None
		if column == '':
			column = None

		self.schema[schema].add_metadata(metadata=metadata, table=table, column=column)
