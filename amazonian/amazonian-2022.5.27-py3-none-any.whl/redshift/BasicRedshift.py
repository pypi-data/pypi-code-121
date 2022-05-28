from sqlalchemy import create_engine, text
import time
from numpy import dtype as numpy_dtype
from pandas import read_sql_query, concat, DataFrame
import psycopg2
from .get_redshift_create_table_query import get_redshift_create_table_query


class BasicRedshift:
	def __init__(self, user_id, password, server, database, port='5439'):
		"""
		:type server: str
		:type port: str
		:type database: str
		:type user_id: str
		:type password: str
		"""
		self._server = server
		self._port = port
		self._database = database
		self._user_id = user_id
		self._password = password
		self._engine = create_engine(self._engine_string)

	def __getstate__(self):
		return {
			'server': self._server,
			'port': self._port,
			'database': self._database,
			'user_id': self._user_id,
			'password': self._password
		}

	def __setstate__(self, state):
		self._server = state['server']
		self._port = state['port']
		self._database = state['database']
		self._user_id = state['user_id']
		self._password = state['password']
		self._engine = create_engine(self._engine_string)

	@property
	def _engine_string(self):
		return f'postgresql://{self._user_id}:{self._password}@{self._server}:{self._port}/{self._database}'

	@property
	def name(self):
		return self._database

	def __str__(self):
		return f'{self._server}/{self.name}'

	def run(self, query):
		connection = None
		try:
			connection = psycopg2.connect(f"""
				dbname='{self._database}' port='{self._port}' 
				user='{self._user_id}' password='{self._password}' 
				host='{self._server}'
			""")
			cursor = connection.cursor()
			cursor.execute(query)
			connection.commit()
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
		finally:
			if connection is not None:
				connection.close()

	def change_password(self, new_password):
		"""
		:type new_password: str
		:return:
		"""
		the_query = "ALTER USER " + self._user_id + " PASSWORD " + "'" + new_password + "'"
		connection = self._engine.connect()
		result = connection.execute(text(the_query))
		self._password = new_password
		return result

	def get_dataframe(self, query, echo=1):
		"""
		:type query: str
		:type echo: int
		:return:
		"""
		start_time = time.time()
		if echo:
			print('\n', query, '\n', sep='')

		result = read_sql_query(query, self._engine)
		elapsed_time = time.time() - start_time
		if elapsed_time >= 3600:
			elapsed_time = elapsed_time / 3600
			time_unit = 'hours'
		elif elapsed_time >= 60:
			elapsed_time = elapsed_time / 60
			time_unit = 'minutes'
		else:
			time_unit = 'seconds'

		if echo:
			print(f'shape:{result.shape}  elapsed time:{round(elapsed_time, 2)}{time_unit}')

		return result


	# schemas:
	_schemas_query = "select * from pg_namespace where nspowner<>'1';"

	def get_schemas(self, echo=1):
		"""
		:type echo: int
		:return:
		"""
		the_query = self._schemas_query
		return self.get_dataframe(query=the_query, echo=echo).sort_values('nspname')

	# tables:
	def _get_tables_data_depricated(self, echo=1):
		the_query = """
			SELECT table_schema AS "schema", table_name AS "table", table_type AS "type" 
			FROM SVV_TABLES WHERE table_schema NOT IN ('admin', 'information_schema', 'metadata', 'public') 
			AND table_schema NOT LIKE 'pg_%%' AND table_type IN ('BASE TABLE', 'VIEW') 
			ORDER BY table_schema, table_name
		"""

		return self.get_dataframe(query=the_query, echo=echo)

	# counts the number of cases with similar values for columns
	# it's good for finding non-unique cases
	def count_similar_rows(self, schema, table, columns, echo=1):
		"""
		:type schema: str
		:type table: str
		:type columns: list of str
		:type echo: int
		:rtype: DataFrame
		"""
		columns_query = '"' + '", "'.join(columns) + '"'

		query = 'SELECT ' + columns_query + ', COUNT(*) AS n '
		query += 'FROM ' + schema + '.' + table + ' GROUP BY ' + columns_query + ' ORDER BY n DESC;'
		return self.get_dataframe(query, echo=echo)

	# close?
	def close(self):
		self._engine.dispose()

	def get_table_scrape_dates_query(self, schema, table, period='month', scrape_date_column='scrape_date'):
		"""
		:type schema: str
		:type table: str
		:type period: str
		:type scrape_date_column: str
		:rtype: str
		"""

		if period == 'year':
			the_query = (
					'SELECT "schema", "table", "year", COUNT(*) AS rows FROM --\n'
					'( --\n'
					'    SELECT --\n'
					'        \'' + schema + '\' AS "schema", --\n'
					'        \'' + table + '\' AS "table", --\n'
					'        DATEPART(year, "' + scrape_date_column + '") AS "year", --\n'
					'        DATEPART(month, "' + scrape_date_column + '") AS "month" --\n'
					'    FROM ' + self._database + '.' + schema + '.' + table + ' --\n'
					') X GROUP BY "schema", "table", "year"'
			)
		elif period == 'month':
			the_query = (
					'SELECT "schema", "table", "year", "month", COUNT(*) AS rows FROM --\n'
					'( --\n'
					'    SELECT --\n'
					'        \'' + schema + '\' AS "schema", --\n'
					'        \'' + table + '\' AS "table", --\n'
					'        DATEPART(year, "' + scrape_date_column + '") AS "year", --\n'
					'        DATEPART(month, "' + scrape_date_column + '") AS "month" --\n'
					'    FROM ' + self._database + '.' + schema + '.' + table + ' --\n'
					') X GROUP BY "schema", "table", "year", "month"'
			)
		else:
			the_query = (
					'SELECT "schema", "table", "date", COUNT(*) AS rows FROM --\n'
					'( --\n'
					'    SELECT --\n'
					'        \'' + schema + '\' AS "schema", --\n'
					'        \'' + table + '\' AS "table", --\n'
					'        TRUNC("' + scrape_date_column + '") AS "date" --\n' 
					'    FROM ' + self._database + '.' + schema + '.' + table + ' --\n'
					') X GROUP BY "schema", "table", "date" '
			)
		return the_query

	def get_table_scrape_dates(self, schema, table, period='month', scrape_date_column='scrape_date', echo=1):
		"""
		:type schema: str
		:type table: str
		:type period: str
		:type scrape_date_column: str
		:type echo: int
		:rtype: DataFrame
		"""
		the_query = self.get_table_scrape_dates_query(
			schema=schema, table=table, period=period,
			scrape_date_column=scrape_date_column
		)
		return self.get_dataframe(query=the_query, echo=echo)

	def get_scrape_dates(self, schema=None, period='month', scrape_date_column='scrape_date', echo=1):
		"""
		:type schema: str
		:type period: str
		:type scrape_date_column: str
		:type echo: int
		:rtype: DataFrame
		"""
		tables_columns = self.get_columns_data(schema=schema, echo=echo)

		scrape_date_tables = tables_columns[tables_columns['column'] == scrape_date_column]

		the_queries = scrape_date_tables.apply(
			lambda x: self.get_table_scrape_dates_query(
				schema=x['schema'], table=x['table'], period=period,
				scrape_date_column=scrape_date_column
			),
			axis=1
		)

		union_query = " UNION --\n".join(the_queries)

		if period == 'year':
			order_query = ' ORDER BY "schema", "table", "year", "month" '
		elif period == 'month':
			order_query = ' ORDER BY "schema", "table", "year" '
		else:
			order_query = ' ORDER BY "schema", "table", "date" '

		return self.get_dataframe(query=union_query + '--\n' + order_query, echo=echo)

	def create_table2(self, data, name, schema, index=False, if_exists='replace'):
		"""
		:type data: DataFrame
		:type name: str
		:type schema: str
		:type index:
		:type if_exists: str
		"""
		null_data = data.iloc[[0], :]
		max_data = data.iloc[[0], :]
		for col in data.columns:
			if any(data[col].isnull()):
				null_data[col] = None
			if data[col].dtype in [numpy_dtype('float64'), numpy_dtype('int64')]:
				max_data[col] = data[col].max()
			else:
				max_string_length = int(data[col].str.len().max())
				max_data[col] = 'x'*(max_string_length+1)
		temp_data = concat([null_data, max_data])
		print(temp_data)
		temp_data.to_sql(name=name, schema=schema, con=self._engine, index=index, if_exists=if_exists)

	def create_table(self, data, name, schema):
		query = get_redshift_create_table_query(database=self.name, schema=schema, table=name, data=data)
		self.run(query=query)
		return query

	def get_errors(self, limit=10, echo=1):
		"""
		:type limit: int
		:type echo: int
		:rtype: DataFrame
		"""
		the_query = (
			"SELECT --\n"
			"	starttime, err_reason, filename, colname, type, --\n"
			"	line_number, position, col_length, raw_field_value, raw_line --\n"
			"FROM stl_load_errors order by starttime desc LIMIT {};"
		).format(limit)

		return self.get_dataframe(query=the_query, echo=echo)

	def get_columns_data(self, schema=None, echo=1):
		"""
		:type schema: str
		:type echo: int
		:rtype: DataFrame
		"""

		the_query = self.columns_query
		order_query = 'ORDER BY datname, nspname, relname, attname;'

		if schema is not None:
			the_query += 'AND TRIM(pg_namespace.nspname) = \'' + schema + '\' '

		the_query += order_query

		result = self.get_dataframe(the_query, echo=echo)
		return result[~result['table'].str.startswith('#')]

	@property
	def columns_query(self):
		_columns_query = (
			'SELECT DISTINCT --\n'
			'	TRIM(pg_database.datname) AS "database",  --\n'
			'	TRIM(pg_namespace.nspname) AS "schema",  --\n'
			'	TRIM(pg_class.relname) AS "table",  --\n'
			'	TRIM(pg_attribute.attname) AS "column" --\n'
			'FROM pg_class '
			'LEFT JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace --\n'
			'LEFT JOIN stv_tbl_perm ON pg_class.oid = stv_tbl_perm.id --\n'
			'LEFT JOIN pg_database ON pg_database.oid = stv_tbl_perm.db_id --\n'
			'LEFT JOIN pg_attribute ON pg_attribute.attrelid = stv_tbl_perm.id --\n'
			'WHERE TRIM(pg_database.datname) = \'' + self._database + '\' '
		)
		return _columns_query

	def get_tables_data_query(self, schema=None):
		"""
		:type schema: str
		:rtype: str
		"""
		if schema is not None:
			where_clause = f'WHERE "schema" = \'{schema}\' '
		else:
			where_clause = ''

		the_query = f"""
			SELECT 
				X.id AS table_id, 
				X."database", 
				X."schema", 
				X."table", 
				X."rows" AS "num_rows", 
				COUNT(DISTINCT pg_attribute.attname) AS "num_columns", 
				ISNULL(size_table.mbytes, 0) AS mbytes 
			FROM 
			( 
				SELECT  
					stv_tbl_perm.id, 
					TRIM(pg_database.datname) AS "database", 
					TRIM(pg_namespace.nspname) AS "schema", 
					TRIM(pg_class.relname) AS "table", 
					SUM(stv_tbl_perm.rows) AS "rows" 
				FROM pg_class 
				LEFT JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace 
				LEFT JOIN stv_tbl_perm ON pg_class.oid = stv_tbl_perm.id 
				LEFT JOIN pg_database ON pg_database.oid = stv_tbl_perm.db_id 
				WHERE TRIM(pg_database.datname) =\'{self._database}\' GROUP BY id, datname, nspname, relname 
			) X 
			LEFT JOIN 
			( 
				SELECT tbl as id, COUNT(*) AS mbytes FROM stv_blocklist GROUP BY tbl 
			) size_table ON size_table.id = X.id 
			LEFT JOIN pg_attribute ON pg_attribute.attrelid = X.id 
			{where_clause} 
			GROUP BY table_id, "database", "schema", "table", "rows", mbytes 
			ORDER BY "database", "schema", "table", "rows"; 

		"""
		return the_query

	def get_tables_data(self, schema=None, echo=0):
		result = self.get_dataframe(query=self.get_tables_data_query(schema=schema), echo=echo)
		return result[~result['table'].str.startswith('#')]
