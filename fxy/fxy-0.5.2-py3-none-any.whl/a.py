# Actuarial

try:
    import numpy
    import numpy as np
except:
    pass

try:
    import pandas
    import pandas as pd
except:
    pass

try:
    import xarray
    import xarray as xr
except:
    pass

try:
    import scipy
    from . import __scipy__ as sp
    import scipy.stats as st
except:
    pass

try:
    import statsmodels
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
except:
    pass

# And plotting
# from fxy.p import *
