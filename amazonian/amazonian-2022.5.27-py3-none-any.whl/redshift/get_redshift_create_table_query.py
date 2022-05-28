from collections import OrderedDict
from math import log2, ceil

def get_data_types(data):
	"""
	returns a dictionary with column names and their respective data types
	:param pandas.DataFrame data: a dataframe
	:rtype: dict[str,str]
	"""
	dtypes = data.dtypes
	return OrderedDict(zip(dtypes.index, dtypes.astype(str)))

def get_redshift_data_types(data):
	"""
	returns a dictionary with column names and their respective redshift data types
	:param pandas.DataFrame data: a dataframe
	:rtype: dict[str,str]
	"""
	data_types = get_data_types(data)
	redshift_data_types = OrderedDict()
	for column, data_type in data_types.items():
		if data_type.startswith('int'):
			redshift_data_types[column] = 'INTEGER'
		elif data_type.startswith('float'):
			redshift_data_types[column] = 'REAL'
		elif data_type.startswith('datetime'):
			redshift_data_types[column] = 'TIMESTAMP'
		elif data_type.startswith('bool'):
			redshift_data_types[column] = 'BOOLEAN'
		else:
			max_length = int(max([len(bytes(str(x), 'utf-8')) for x in data[column].values]))
			nearest_power_of_two = 2 ** ceil(log2(max_length+1))-1
			redshift_data_types[column] = f'VARCHAR({nearest_power_of_two})'
	return redshift_data_types

def get_redshift_create_table_query(database, schema, table, data, data_types=None):
	"""
	:param str database: name of database
	:param str schema: name of schema
	:param str table: name of table
	:param pandas.DataFrame data: data to be uploaded
	:param dict[str,str] data_types: a dictionary of the redshift data types
	:rtype: str
	"""
	data_types = data_types or get_redshift_data_types(data=data)
	data_types_str = ', \n'.join([f'"{col}" {dtype}' for col, dtype in data_types.items()])
	return f"""
		CREATE TABLE IF NOT EXISTS {database}.{schema}.{table} (
			{data_types_str}
		)
	"""
