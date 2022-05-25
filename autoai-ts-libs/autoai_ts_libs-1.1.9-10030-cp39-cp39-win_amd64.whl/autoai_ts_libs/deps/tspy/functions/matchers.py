"""
main entry point for all sequence and item-set matchers
"""


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
from autoai_ts_libs.deps.tspy import _get_context
from autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.ItemSetMatcher import ItemSetMatcher
from autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.SequenceMatcher import SequenceMatcher


def subset(threshold=0.0, matcher_threshold="PS"):
    """Creates a matcher that matches an array of string values (the pattern) with a string time series, regardless of the
    order in which the items in the pattern occur in the time series.

    Parameters
    ----------
    threshold : float, optional
        indicates the minimum ratio by matcher_threshold type. (default is 0.0)
    matcher_threshold : str, optional
        the threshold type, one of PS (pattern / sequence), PM (pattern / match), MS (match / sequence). (default is PS)

    Returns
    -------
    matcher
        a new matcher
    """
    tsc = _get_context()
    if matcher_threshold.lower() == "ps":
        j_mt = tsc.packages.time_series.ml.sequence_mining.containers.MatcherThreshold.PS
    elif matcher_threshold.lower() == "pm":
        j_mt = tsc.packages.time_series.ml.sequence_mining.containers.MatcherThreshold.PM
    elif matcher_threshold.lower() == "ms":
        j_mt = tsc.packages.time_series.ml.sequence_mining.containers.MatcherThreshold.MS
    else:
        raise Exception("must be one of ps, pm, ms")
    return ItemSetMatcher(tsc,
                          tsc.packages.time_series.ml.itemset_mining.functions.ItemSetMatchers.subset(threshold,
                                                                                                            j_mt))


def seq():
    """Creates a matcher that matches an array of string values (the pattern) with an entire string time series exactly
    and in sequence

    Returns
    -------
    matcher
        a new matcher
    """
    tsc = _get_context()
    return SequenceMatcher(tsc, tsc.packages.time_series.ml.sequence_mining.functions.SequenceMatchers.seq())


def subseq(threshold=0.0, matcher_threshold="PS"):
    """Creates a matcher that matches an array of string values (the pattern) with a sub-sequence of a string time
    series, to within the specified coverage threshold.

    Parameters
    ----------
    threshold : float, optional
        indicates the minimum ratio by matcher_threshold type. (default is 0.0)
    matcher_threshold : str, optional
        the threshold type, one of PS (pattern / sequence), PM (pattern / match), MS (match / sequence). (default is PS)

    Returns
    -------
    matcher
        a new matcher
    """
    tsc = _get_context()
    if matcher_threshold.lower() == "ps":
        j_mt = tsc.packages.time_series.ml.sequence_mining.containers.MatcherThreshold.PS
    elif matcher_threshold.lower() == "pm":
        j_mt = tsc.packages.time_series.ml.sequence_mining.containers.MatcherThreshold.PM
    elif matcher_threshold.lower() == "ms":
        j_mt = tsc.packages.time_series.ml.sequence_mining.containers.MatcherThreshold.MS
    else:
        raise Exception("must be one of ps, pm, ms")
    return SequenceMatcher(tsc,
                           tsc.packages.time_series.ml.sequence_mining.functions.SequenceMatchers.subseq(
                               threshold, j_mt))


def sublist(threshold=0.0):
    """Creates a matcher that matches an array of string values (the pattern) with a sublist of a string time series, to
    within the specified coverage threshold.

    Parameters
    ----------
    threshold : float, optional
        indicates the minimum ratio by matcher_threshold type. (default is 0.0)

    Returns
    -------
    matcher
        a new matcher
    """
    tsc = _get_context()
    return SequenceMatcher(tsc, tsc.packages.time_series.ml.sequence_mining.functions.SequenceMatchers.sublist(threshold))
