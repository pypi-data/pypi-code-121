"""#
Doc::


Sequential bootstraping
https://nbviewer.ipython.org/github/bashtage/arch/blob/main/examples/bootstrap_examples.ipynb

https://quantdare.com/bootstrapping-time-series-data/

Block Bootstraping

https://lbelzile.github.io/timeseRies/boostrap-methods-for-time-series.html


# Import data
import datetime as dt
import pandas as pd
import numpy as np
import pandas_datareader.data as web
start = dt.datetime(1951,1,1)
end = dt.datetime(2014,1,1)
sp500 = web.get_data_yahoo('^GSPC', start=start, end=end)
start = sp500.index.min()
end = sp500.index.max()
monthly_dates = pd.date_range(start, end, freq='M')
monthly = sp500.reindex(monthly_dates, method='ffill')
returns = 100 * monthly['Adj Close'].pct_change().dropna()

# Function to compute parameters
def sharpe_ratio(x):
    mu, sigma = 12 * x.mean(), np.sqrt(12 * x.var())
    return np.array([mu, sigma, mu / sigma])

# Bootstrap confidence intervals
from arch.bootstrap import IIDBootstrap
bs = IIDBootstrap(returns)
ci = bs.conf_int(sharpe_ratio, 1000, method='percentile')



"""



def bootstrap_sequential():
  """Sequential.
  Doc::

      # Import data
      # Function to compute parameters
      def sharpe_ratio(x):
          mu, sigma = 12 * x.mean(), np.sqrt(12 * x.var())
          return np.array([mu, sigma, mu / sigma])

      # Bootstrap confidence intervals
      from arch.bootstrap import IIDBootstrap
      bs = IIDBootstrap(returns)
      ci = bs.conf_int(sharpe_ratio, 1000, method='percentile')

     Bootstrap
        Bootstraps
        IID Bootstrap
        Stationary Bootstrap
        Circular Block Bootstrap
        Moving Block Bootstrap
        Methods
        Confidence interval construction
        Covariance estimation
        Apply method to estimate model across bootstraps
        Generic Bootstrap iterator



  """
  pass