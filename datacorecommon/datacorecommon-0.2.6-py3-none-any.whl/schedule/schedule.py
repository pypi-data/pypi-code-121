# Dependencies
######################

def set_datetimewindow(datetime_begin: str, datetime_end: str, datetime_init: str, path_sink: str, load_mode: str='incremental'):
    """
    Define begin_datetime and end_datetime based on given load_mode, begin input, end input and destination path.
    1. Define datetime_begin
        Based on given load modes (incremental, full, input)
        incremental:
        First run (if destination does not exist yet): set the datetime_begin to datetime_init (full load).
        Next run: set datetime_begin to the max __ts_etl date of the destination delta table
        full:
        Set the datetime_begin to datetime_init (Full load).
        input:
        Set datetime_begin to datetime_begin input converted to datetime if given a string input, else use given datetime object.
        
    2. Define datetime_end
        Set datetime_end to datetime_end input converted to datetime if given a string input, else use given datetime object.
        
    Parameters
    ----------
    datetime_begin : str
        Either a blank string or an ISO-8601 timestamp to define the beginning of the extraction window.
    datetime_end : str
        An ISO-8601 timestamp to define the end of the extraction window.
    datetime_init: str
        An ISO-8601 timestamp to define the minimum date of the extraction window in case of a full load (business rule).
    path_destination : str, 
        Path of the destination
    load_mode : str, optional
        The mode which will be used to define begin and end datetime (default is incremental)
        
    Returns
    -------
    datetime, datetime
        begin_datetime and end_datetime object
    """
    import datetime
    from .._helpers import _assert_iso8601
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.getOrCreate()

    # Assert that timestamp strings are in ISO-8601
    _assert_iso8601(datetime_end)
    _assert_iso8601(datetime_init)
    
    # Define datetime_begin from the load_mode
    if load_mode.lower() == 'incremental':
        try:
            datetime_begin = spark.sql(f'SELECT MAX(__ts_etl) AS MAX_DATE FROM delta.`{path_sink}`').first()['MAX_DATE']
        except:
            datetime_begin = datetime.datetime.strptime(datetime_init, '%Y-%m-%d %H:%M:%S')
        
    elif load_mode.lower() == 'full':
        datetime_begin = datetime.datetime.strptime(datetime_init, '%Y-%m-%d %H:%M:%S')
        
    elif load_mode.lower() == 'input':
        if datetime_begin != '':
            _assert_iso8601(datetime_begin)
            datetime_begin = datetime.datetime.strptime(datetime_begin, '%Y-%m-%d %H:%M:%S')
        else:
            raise NotImplementedError('Empty datetime_begin for load_mode input')
        
    else:
        raise NotImplementedError('Invalid or empty load_mode')
        
    # Define datetime_end
    datetime_end = datetime.datetime.strptime(datetime_end, '%Y-%m-%d %H:%M:%S')
    
    return datetime_begin, datetime_end
