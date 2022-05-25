# Dependencies
######################
import pyspark.sql.functions as F
from pyspark.sql.window import Window

def compute_cagr(_df, _col, _yearcol, _years=3, _partitioncols=None):
  """
  Compute the compound annual growth rate (CAGR) for the values in column _col for a period of _years.  See https://en.wikipedia.org/wiki/Compound_annual_growth_rate for more information on CAGR.
  Uses a pyspark.sql.window.Window under the hood to determine the lagged value.

  Parameters
    ----------
    _df: :class:`~pyspark.sql.dataframe`
        The PySpark dataframe on which to run the computations on.  It is expected that the columns _col, _yearcol and _partitioncols are columns in this dataframe.
    _col: str
        The name of the column for which to compute the CAGR.  The values in the column are expected to be numeric.
    _yearcol: str
        The name of the column which contains the year information.  The values in the column are expected to be numeric.
    _years: int
        The number of years over which to compute the CAGR.  Default is 3 years.
    _partitioncols: list, optional
        The columns needed to correctly use pyspark.sql.window.Window.partitionBy.
  """

  # Define the SQL window needed to compute the lagged values
  if _partitioncols == None:
      _ws = Window.orderBy(_yearcol)
  elif (type(_partitioncols) == list) & (len(_partitioncols) >=1):
        _ws = Window.partitionBy(*_partitioncols).orderBy(_yearcol)
  else:
        raise TypeError('The partition columns are not correctly set.  Was expecting a list or None')

  # Get the lagged values
  _df = _df.withColumn('___lag___', F.lag(_col, offset=_years).over(_ws))
  
  # CAGR computation
  _df = _df.withColumn(_col +'_CAGR_{}'.format(_years),
                       (F.col(_col) / F.col('___lag___')) ** (1/_years) - 1
                      )
  
  # Drop unneeded columns
  _df = _df.drop('___lag___')
  
  return _df