"""
main entry-point for creation of :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`
"""
from autoai_ts_libs.deps.tspy import _get_context
from autoai_ts_libs.deps.tspy._others import builder

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
from autoai_ts_libs.deps.tspy.data_structures import BoundTimeSeries
import autoai_ts_libs.deps.tspy.dtypes



def _empty(tsc):
    """creates an empty observation-collection

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries.BoundTimeSeries`
        a new observation-collection
    """
    return BoundTimeSeries(tsc)

def _of(*observations):
    """creates a collection of observations

    Parameters
    ----------
    observations : varargs
        a variable number of observations

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries.BoundTimeSeries`
        a new observation-collection
    """
    ts_builder = builder()
    for obs in observations:
      if isinstance(obs, autoai_ts_libs.deps.tspy.dtypes.Observation):
        ts_builder.add(obs)
      elif isinstance(obs, list):
        for ob in obs:
          ts_builder.add(ob)
    return ts_builder.result()

def observations(*varargs):
    """returns an :class:`.ObservationCollection`

    Parameters
    ----------
    observations : varargs
        either empty or a variable number of observations

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries.BoundTimeSeries`
        a new observation-collection
    """
    tsc = _get_context()
    if len(varargs) > 0:
        return _of(*varargs)
    else:
        return _empty(tsc)
