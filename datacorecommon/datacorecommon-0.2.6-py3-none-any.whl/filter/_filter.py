# Dependencies
######################
import pyspark.sql.functions as F
from pyspark.sql.window import Window

# Type setting
######################

# Functions
######################
def _apply_rankfilter(_df, _partitioncols, _ordercols, _rank=1):
    """
    Apply a ranking over a SQL window and filter all records out which do not have _rank.

    Returns a filtered dataframe with all columns but filtered to _rank.

     Parameters
    ----------
    _df: :class:`~pyspark.sql.dataframe`
        The PySpark dataframe on which to run the computations on.  It is expected that the columns specified in _partitioncols and in _ordercols are present in this dataframe.
    _partitioncols: str or list
        The column name or list of column names that are keys for the dataframe.
    _ordercols: str or list
        The column or list of `~pyspark.sql.column`s that order the dataframe.
    """

    # Generate the window
    _windowspec = Window.partitionBy(*_partitioncols).orderBy(*_ordercols)
  
    # Perform ranking and filtering
    _df = _df.withColumn('___RANK___', F.rank().over(_windowspec))
    _df = _df.filter(F.col('___RANK___') == _rank)

    return _df.drop('___RANK___')


def takelatestrecordperkey(_df, _partitioncols, _ordercols):
    """
    Take the latest record of the DataFrame partitioned by _partitioncols and ordered *descendingly* along _ordercols.
    
    Returns a filtered dataframe with all columns but limited to the latest record per key.

    Parameters
    ----------
    _df: :class:`~pyspark.sql.dataframe`
        The PySpark dataframe on which to run the computations on.  It is expected that the columns specified in _partitioncols and in _ordercols are present in this dataframe.
    _partitioncols: str or list
        The column name or list of column names that are keys for the dataframe.
    _ordercols: str or list
        The column name or list of column names to order the dataframe.  Defaults to orderring *all* the columns descendingly.
    """
    from .._helpers import _convert_to_list

    _partitioncols = _convert_to_list(_partitioncols)
    _ordercols = _convert_to_list(_ordercols)
    _ordercols = [F.col(col).desc() for col in _ordercols]
  
    return _apply_rankfilter(_df, _partitioncols, _ordercols, _rank=1)

def takefirstrecordperkey(_df, _partitioncols, _ordercols):
    """
    Take the first record of the DataFrame partitioned by _partitioncols and ordered *ascendingly* along _ordercols.

    Returns a filtered dataframe with all columns but limited to the latest record per key.

    Parameters
    ----------
    _df: :class:`~pyspark.sql.dataframe`
        The PySpark dataframe on which to run the computations on.  It is expected that the columns specified in _partitioncols and in _ordercols are present in this dataframe.
    _partitioncols: str or list
        The column name or list of column names that are keys for the dataframe.
    _ordercols: str or list
        The column name or list of column names to order the dataframe.  Defaults to orderring *all* the columns ascendingly.
    """
    from .._helpers import _convert_to_list

    _partitioncols = _convert_to_list(_partitioncols)
    _ordercols = _convert_to_list(_ordercols)  
    
    return _apply_rankfilter(_df, _partitioncols, _ordercols, _rank=1)