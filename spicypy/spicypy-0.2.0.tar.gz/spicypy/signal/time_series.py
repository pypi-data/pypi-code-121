"""
Class extending functionality of :obj:`gwpy.timeseries.timeseries.TimeSeries` from GWpy

Artem Basalaev <artem[dot]basalaev[at]physik.uni-hamburg.de>,
Christian Darsow-Fromm <cdarsowf[at]physnet.uni-hamburg.de>
"""
from gwpy.timeseries import TimeSeries as ts


class TimeSeries(ts):
    """
    Class to model signals (time series)

    """
