# Dependencies
######################
import delta.tables
import datetime
from pyspark.sql import SparkSession


spark = SparkSession.builder.getOrCreate()


# Type setting
######################

# Helpers
######################
def _null_safe_expr(table_right: str, table_left: str, _columns):
  '''
  Create an expression used to join two dataframes on given collumns which can include nulls.
  The function returns an expression in the following fromat:
  (table_right.col1 <=> table_left.col1) AND (table_right.col2 <=> table_left.col2)
  '''

  mylist = ['({}.{} <=> {}.{})'.format(str(table_right), cc, str(table_left), cc) for cc in _columns]
  return ' AND '.join(mylist)


def _define_change_cols(table_exist, change_cols: list, no_change_cols: list, tech_cols: list):
    '''
    Define change cols
    '''
    if change_cols == None:
        change_cols = table_exist.toDF().columns
        change_cols = [cc for cc in change_cols if cc not in tech_cols]

    if no_change_cols != None:
        change_cols = [cc for cc in change_cols if cc not in no_change_cols]
    return change_cols


def _define_val_and_set_values(table_exist, valid_from_col: str, valid_until_col: str, ts_col: str, ts_col_src: str):
    '''
    Define insert and update values
    '''
    val_inserts = {valid_until_col: 'null'}
    if ts_col_src == None:
        val_inserts[valid_from_col] = f'staged_updates.{ts_col}'
        val_updates = {valid_until_col: f'staged_updates.{ts_col}'}

    else:
        val_inserts[valid_from_col] = f'staged_updates.{ts_col_src}'
        val_updates = {valid_until_col: f'staged_updates.{ts_col_src}'}

    update_cols = table_exist.toDF().columns
    update_cols = [cc for cc in update_cols if cc not in [valid_from_col, valid_until_col]]

    for cc in update_cols:
        val_inserts[cc] = f'staged_updates.{cc}'

    return val_inserts, val_updates

# Functions
######################
def delta_readfile(_path: str):
    """
    Read the Delta Lake file stored at the specified path.

    Additional keyword arguments are not supported
    """
    return spark.read.format('delta').load(_path)


def delta_writefile(_df, _path: str, _writemode='append', _cond=None, _partition=False, _partcols=[], **kwargs):
    """
    Write out the PySpark dataframe _df to the specified _path as a Databricks Delta Lake file.

    Different types of writing behaviour are supported:
    _writemode='overwrite':  overwrites existing Delta Lake files at the specified _path with the dataframe
    _writemode='append':     appends the dataframe to the existing Delta Lake files (default)
    _writemode='ignore':     does not write out any data if files exist at the _path location (allows for integration testing)
    _writemode='insert_all': appends the dataframe to the existing Delta Lake files and inserts complete rows for all matches rows according to the condition
    _writemode='insert_none':appends the dataframe to the existing Delta Lake files and inserts *no* rows for all matches rows according to the condition
    _writemode='insert_specific': not yet supported

    **Note**: the original table needs to be referred as "table" for the insert condition and the new table as "updates"

    Setting the _partitioning of the Delta Lake file during overwrite write mode is supported.  Any existing partitioning will be automatically followed during all other write modes.
    _partition: boolean to indicate whether partitioning is needed
    _partcols:  list of column names to be used for partitioning
    """
    assert _writemode in ['overwrite', 'append', 'ignore', 'insert_all', 'insert_none'], 'Illegal _writemode specified'

    # Default Parquet behaviour
    if _writemode in ['overwrite', 'append', 'ignore']:
        _conn = (_df.write
                 .format('delta')
                 .mode(_writemode)
                 )
        # Overwrite behaviour:
        if _writemode == 'overwrite':
            _conn = _conn.option('overwriteSchema', 'true')

        # Include partioning
        if _partition:
            _conn = _conn.partitionBy(_partcols)

        # Work with the additional keyword arguments
        for _key, _val in kwargs.items():
            _conn = _conn.option(_key, _val)

        _conn.save(_path)
        return

    # WhenMatchedInsertAll behaviour
    elif _writemode == 'insert_all':
        # Connect to the existing table
        _table = delta.tables.DeltaTable.forPath(spark, _path)

        # Create an execution plan
        _plan = (_table
                 .alias('table')
                 .merge(_df.alias('updates'), _cond)
                 .whenMatchedUpdateAll()
                 .whenNotMatchedInsertAll()
                 )
        _plan.execute()
        return

    # WhenMatchedInsertNone behaviour
    elif _writemode == 'insert_none':
        # Connect to the existing table
        _table = delta.tables.DeltaTable.forPath(spark, _path)

        # Create an execution plan
        _plan = (_table
                 .alias('table')
                 .merge(_df.alias('updates'), _cond)
                 .whenNotMatchedInsertAll()
                 )
        _plan.execute()
        return


def delta_writefile_scd2(_df, _path: str, _writemode: str, id_col: str, ts_col: str,
                         ts_col_src: str = None, ts_col_first: str = None, ts_first: datetime.datetime = None, change_cols: list = None,
                         no_change_cols: list = None,
                         valid_from_col: str = '__ts_valid_from', valid_until_col: str = '__ts_valid_until'):
    '''
    This function compares an incoming dataframe with an existing delta table based on a given path.
    In case of _writemode 'overwrite':
      Destination delta table will be overwritten with all incoming records.
      These records will be given a valid_until_date based on if you specified ts_col_first or ts_first.
        <IMPORTANT: Always use either ts_col_first or ts_first>

    In case of _writemode 'scd2':
      The function will insert and update records based on the SCD Type 2 method.
      The function compares incoming records with existing records.
      Based on the comparison, it defines INSERT and UPDATE records.
      INSERT records:
        It inserts all incoming records which meet the following condition at the comparison:
          - No matching ID
          OR
          - Matching ID
            AND at least one change in the change_cols
              If no change_cols are specified, the function uses all columns except for [id_col, ts_col, ts_col_src, valid_from_col, valid_until_col]

        The insert records get a valid_from_date based on if you specified ts_col_src or not.
        When specified: valid_from_date will be ts_col_src.
        Else: valid_from_date will be ts_col.

      UPDATE records:
        It updates all existing records which meet the following condition at the comparison:
          - Matching ID
            AND at least one change in the change_cols
              If no change_cols are specified, the function uses all columns except for [id_col, ts_col, ts_col_src, valid_from_col, valid_until_col]
            AND Valid_until_date is null

        The update records get a valid_until_date based on if you specified ts_col_src or not.
        When specified: valid_until_date will be ts_col_src.
        Else: valid_until_date will be ts_col.

    Source: https://sanajitghosh.medium.com/slowly-changing-dimensions-scd-using-databricks-python-sql-f6cd5fbc2f

    Parameters
    ----------
    _df: dataframe
      Incoming dataframe with change statements
    _path: str
      Existing dataframe path
    _writemode:str
      Current supported writemodes: 'overwrite' AND 'scd2'
    id_col: list
      Column name, used as a unique identifier
    ts_col: str
      Column name, used for timestamp of the ETL
    ts_col_src: str
      Column name, used for timestamp of the original source data update date
      If None: Function will use ts_col instead
    ts_col_first: str
      Column name, used for first valid_from_date of the record
      If None: use ts_first
    ts_first: dt.datetime
      Datetime set as first valid_from_date of every record
    change_cols: list
      List of column names which will be used to check on changes (string)
      If None: Use all columns except for id_col, valid_from_col and valid_until_col
    no_change_cols: list
      List of column names which will not be used to check on changes (string)
      If None: no columns will be removed from change_cols
    valid_from_col: str (default = '__ts_valid_from')
      Column name, which indicates when a records is valid from
    valid_until_col: str (default = '__ts_valid_until')
      Column name, which indicates when a records is valid until
    Returns
    -------
    dataframe
    '''    
    from pyspark.sql import functions as F
    from pyspark.sql import types as T

    assert _writemode in ['overwrite', 'scd2'], 'Illegal _writemode specified'

    if _writemode == 'overwrite':

        # SET VALID FROM/UNTIL VALUES
        #############################
        if ts_col_first == None:
            _df = _df.withColumn(valid_from_col, F.lit(ts_first))
        else:
            _df = _df.withColumn(valid_from_col, F.col(ts_col_first))

        _df = (_df
               .withColumn(valid_until_col, F.lit(None))
               .withColumn(valid_until_col, F.col(valid_until_col).cast(T.TimestampType()))
               )

        # WRITE RECORDS TO DESTINATION DELTA
        ####################################
        delta_writefile(_df=_df,
                        _path=_path,
                        _writemode='overwrite'
                        )

    elif _writemode == 'scd2':
        # Pointer to destination deltatable
        table_exist = delta.tables.DeltaTable.forPath(spark, _path)

        # DETERMINE WHICH COLUMNS NEED TO BE UPDATED
        ############################################
        change_cols = _define_change_cols(table_exist=table_exist,
                                          change_cols=change_cols,
                                          no_change_cols=no_change_cols,
                                          tech_cols=[id_col, ts_col, ts_col_src, valid_from_col, valid_until_col])

        # BUILD DATAFRAME FOR UPDATES
        #############################
        # Define rows to insert
        # They are records that are matched with the ID's in the existing delta table
        df_new_insert = (_df
                         .alias('updates')
                         .join(table_exist.toDF().alias('table'), id_col)
                         .where(f"NOT ({_null_safe_expr('table', 'updates', change_cols)})")
                         .where(f'table.{valid_until_col} is null')
                         )

        # Stage the updates by unioning two sets of rows
        # 1. Rows that will be inserted in the whenNotMatched clause (NULL as mergekey)
        # 2. Rows that will either update the current rows of existing rows or insert the new rows (id_col as mergekey)
        staged_updates = (
            df_new_insert
                .selectExpr('NULL as mergekey', 'updates.*')
                .unionByName(_df.selectExpr(f'{id_col} as mergekey', '*'))
        )

        # DEFINE SPECIFIC UPDATE VALUES
        ###############################
        val_inserts, val_updates = _define_val_and_set_values(table_exist=table_exist,
                                                              valid_from_col=valid_from_col,
                                                              valid_until_col=valid_until_col,
                                                              ts_col=ts_col,
                                                              ts_col_src=ts_col_src)

        # BUILD EXECUTION PLAN
        ######################
        plan = (table_exist
            .alias('table')
            .merge(
              staged_updates.alias('staged_updates'),
              f'table.{id_col} = mergekey'
              )
            .whenMatchedUpdate(
              condition=f"NOT ({_null_safe_expr('table', 'staged_updates', change_cols)}) AND table.{valid_until_col} is null",
              set=val_updates
              )
            .whenNotMatchedInsert(
              values=val_inserts
              )
        )

        # RUN EXECUTION PLAN
        ####################
        plan.execute()

    else:
        raise NotImplementedError(f'_writemode: {_writemode} not implemented')
