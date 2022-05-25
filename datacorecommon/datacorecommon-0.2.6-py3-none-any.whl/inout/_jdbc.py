# Dependencies
######################
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

# Type setting
######################

# Functions
######################
def _jdbc_createconnection(_user:str, _passw:str, _url:str, _driver:str):
  """
  Create a connection to a specified database (connected through JDBC) and return the connection as a result.
  Authentication is based on the user and password combination for the specified database.
  The database is identified through the URL.
  """
  # Create the connection to the database
  _conn = (spark.read.format('jdbc')
           .option('url', _url)
           .option('driver', _driver)
           .option('user', _user)
           .option('password', _passw)
          )
  return _conn


def oracle_executequery(_query:str, _user:str, _passw:str, _url:str):
  """
  Execute a SQL query on the specified Oracle database and return the result as a PySpark dataframe.
  Authentication is based on the user and password combination for the specified database.
  The database is identified through the URL.
  
  Additional keyword arguments are not yet supported
  
  Ensure that the Oracle JDBC driver is installed on your cluster (https://mvnrepository.com/artifact/com.oracle.jdbc)
  """
  # Create the connection to the database
  _conn = _jdbc_createconnection(_user, _passw, _url, _driver='oracle.jdbc.driver.OracleDriver')
  
  # Provide additional settings for an Oracle database
  _conn = _conn.option('oracle.jdbc.timezoneAsRegion', 'false')
    
  # Execute the query and return the result as a dataframe
  return _conn.option('query', _query).load()


def oracle_readtable(_table:str, _user:str, _passw:str, _url:str, **kwargs):
  """
  Read a SQL table from the specified Oracle database and return the result as a PySpark dataframe.
  Authentication is based on the user and password combination for the specified database.
  The database is identified through the URL.
  
  Additional keyword arguments for the JDBC connection (https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html) are supported
  
  Ensure that the Oracle JDBC driver is installed on your cluster (https://mvnrepository.com/artifact/com.oracle.jdbc)
  """
  # Create the connection to the database
  _conn = _jdbc_createconnection(_user, _passw, _url, _driver='oracle.jdbc.driver.OracleDriver')
  
  # Provide additional settings for an Oracle database
  _conn = _conn.option('oracle.jdbc.timezoneAsRegion', 'false')
    
  # Work with the additional keyword arguments
  for _key, _val in kwargs.items():
    _conn = _conn.option(_key, _val)  
    
  # Read the table and return the result as a dataframe
  return _conn.option('dbtable', _table).load()


def postgres_executequery(_query:str, _user:str, _passw:str, _url:str):
  """
  Execute a SQL query on the specified Postgres database and return the result as a PySpark dataframe.
  Authentication is based on the user and password combination for the specified database.
  The database is identified through the URL.
  
  Additional keyword arguments are not yet supported
  
  Ensure that the PostgreSQL JDBC driver is installed on your cluster (https://jdbc.postgresql.org/)
  """
  # Create the connection to the database
  _conn = _jdbc_createconnection(_user, _passw, _url, _driver='org.postgresql.Driver')
      
  # Execute the query and return the result as a dataframe
  return _conn.option('query', _query).load()


def postgres_readtable(_table:str, _user:str, _passw:str, _url:str, **kwargs):
  """
  Read a SQL table from the specified Postgres database and return the result as a PySpark dataframe.
  Authentication is based on the user and password combination for the specified database.
  The database is identified through the URL.
  
  Additional keyword arguments for the JDBC connection (https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html) are supported
  
  Ensure that the PostgreSQL JDBC driver is installed on your cluster (https://jdbc.postgresql.org/)
  """
  # Create the connection to the database
  _conn = _jdbc_createconnection(_user, _passw, _url, _driver='org.postgresql.Driver')
    
  # Work with the additional keyword arguments
  for _key, _val in kwargs.items():
    _conn = _conn.option(_key, _val)  
    
  # Read the table and return the result as a dataframe
  return _conn.option('dbtable', _table).load()


def bigquery_readtable(_project:str, _dataset:str, _table:str, **kwargs):
  """
  Read the BigQuery table from the specified dataset in the corresponding project (identified as {_project}.{_dataset}.{_table}).  Returns the data as a PySpark dataframe.
  
  Additional keyword arguments for the BigQuery connection (https://github.com/GoogleCloudDataproc/spark-bigquery-connector) are supported
  
  **Note**: Defaults to the project of the Service Account being used
  """
  
  # Create the connection to the BigQuery table
  _conn = spark.read.format('bigquery')
  
  # Work with the additional keyword arguments
  for _key, _val in kwargs.items():
    _conn = _conn.option(_key, _val)
    
  # Read the BiqQuery table and return the result as a dataframe
  return _conn.load('{}.{}.{}'.format(_project, _dataset, _table))


def bigquery_writetable(_df, _project:str, _dataset:str, _table:str, _writemode='append', **kwargs):
  """
  Write out the PySpark dataframe _df to the specified BigQuery table.  The BigQuery table is identified as {_project}.{_dataset}.{_table}.
  
  Different types of writing behaviour are supported:
  _writemode='overwrite':  overwrites existing BigQuery table with the dataframe
  _writemode='append':     appends the dataframe to the existing BigQuery table (default)
  
  Additional keyword arguments for the BigQuery connection (https://github.com/GoogleCloudDataproc/spark-bigquery-connector) are supported
  
  **Note**: A temporary GcsBucket is almost always required!
  """
  assert _writemode in ['overwrite', 'append'], 'Illegal _writemode specified'
  
  # Create the connection to the BigQuery table
  _conn = _df.write.format('bigquery')
  
  # Work with the additional keyword arguments
  for _key, _val in kwargs.items():
    _conn = _conn.option(_key, _val)
  
  # Set writemode
  _conn = _conn.mode(_writemode)
  
  # Write out the dataframe
  _conn.save('{}.{}.{}'.format(_project, _dataset, _table))
  return
