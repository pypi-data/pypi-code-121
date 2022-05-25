# Dependencies
######################
import pyspark.sql.functions as F
from pyspark.sql.window import Window

def create_bagofwords_fromtimewindow(_df, _timestampcol, _bagcols, _partitioncols=None, _lagtime=-900, _leadtime=0, _lowerexclusive=False, _upperexclusive=False, _columnname='bagofwords'):
    """
    Function to create a bag of words on certain columns from the PySpark Dataframe using a time window.  This time window is created as [_lagtime, _leadtime] around the current row.  It does so based on the _timestampcol and will create a bag of words for the column in the _bagcols list.  This bag of words is of type ArrayType(StructType), where each element in the array contains the columns from _bagcols.  It is important to note that the result acts an unordered array and might contain duplicate values if these were present in the original dataframe.
    
    Uses a pyspark.sql.window.Window and the pyspark.sql.window.Window.rangeBetween under the hood to create the SQL window.  The rangeBetween uses the explicit unixtimestamp to run these operations.  By first creating the structtype column and only then applying the windowing one can guarantee that the elements in a row of the bagofword column originally belonged together.  Moroever, it also migate some OOM errors compared to creasing a single column per element of _bagcols.
    
    Returns the original dataframe with the bag of words column added.
    
    Parameters
    ----------
    _df: :class:`~pyspark.sql.dataframe`
        The PySpark dataframe on which to run the computations on.  It is expected that the columns _timestampcol, _bagcols and _partitioncols are columns in this dataframe.
    _timestampcol: str
        The name of the column to use as the timestamp for windowing by time.  The data in this column must be of TimestampType.
    _bagcols: list
        List of the name of columns on which to create a bag of words.
    _partitioncols: list, optional
        The columns needed to correctly use pyspark.sql.window.Window.partitionBy.
    _lagtime: int, optional
        Lower boundary of the time window, expressed in seconds.  Default is -900s
    _leadtime: int, optional
        Upper boundary of the time window, expressed in seconds.  Default is 0s
    _lowerexclusive: bool, optional
        Boolean to indicate whether the lower boundary value of the time window needs to be included or not.  If `True`, one second will be subtracted from the the _lagtime.  Default is `False`.
    _upperexclusive: bool, optional
        Boolean to indicate whether the upper boundary value of the time window needs to be included or not.  If `True`, one second will be subtracted from the the _leadtime.  Default is `False`
    _columnname: str, optional
        Name of the column in which the array of struct types is stored.
    """
    from .._helpers import _convert_to_list

    # Create the temporary unixtime column
    _df = _df.withColumn('___UNIXTIME___', F.unix_timestamp(_timestampcol))
    
    # Set boundaries correctly
    if (_lowerexclusive ==True) & (_lagtime > 0):
        _lagtime -= 1
    elif (_lowerexclusive ==True) & (_lagtime == 0):
        _lagtime += 1
    elif (_lowerexclusive ==True) & (_lagtime < 0):
        _lagtime += 1
    
    if (_upperexclusive ==True) & (_leadtime > 0):
        _leadtime -= 1    
    elif (_upperexclusive ==True) & (_leadtime == 0):
        _leadtime -= 1
    elif (_upperexclusive ==True) & (_leadtime < 0):
        _leadtime += 1
    
    # Create the SQL window
    if _partitioncols == None:
        _ws = Window.orderBy('___UNIXTIME___').rangeBetween(_lagtime, _leadtime)
    elif (type(_partitioncols) == list) & (len(_partitioncols) >=1):
        _ws = Window.partitionBy(*_partitioncols).orderBy('___UNIXTIME___').rangeBetween(_lagtime, _leadtime)
    else:
        raise TypeError('The partition columns are not correctly set.  Was expecting a list or None')
    
    # Create the bag of words
    _bagcols = _convert_to_list(_bagcols)
    
    # Create a struct type of the different columns
    _df = _df.withColumn(_columnname, F.struct(*_bagcols))
    
    # Collect the list of this structtype
    _df = _df.withColumn(_columnname, F.collect_list(_columnname).over(_ws))
    
    # Remove the temporary unixtime column
    _df = _df.drop('___UNIXTIME___')
    
    return _df