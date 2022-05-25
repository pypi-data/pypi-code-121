
#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/
from typing import TypeVar
from autoai_ts_libs.deps.tspy import _get_context
from autoai_ts_libs.deps.tspy.data_structures import Observation, BoundTimeSeries, Segment, Prediction

OT = TypeVar('OT', list, tuple, dict, int, float, bool, str, BoundTimeSeries, Observation, Segment, Prediction)

def observation(time_tick, value: OT):
    """
    create an observation

    Parameters
    ----------
    time_tick : int
        observations time-tick
    value : list, tuple, dict
        observations value

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.Observation.Observation`
    """
    tsc = _get_context()
    return Observation(tsc, time_tick, value)

def builder():
    """
    create a time-series builder

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TSBuilder.TSBuilder`
        a new time-series builder
    """
    tsc = _get_context()
    return tsc.java_bridge.builder()
