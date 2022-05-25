# MultiTimeSeries<KEY, List<TERM>> dataMTS, MultiTimeSeries<KEY, DOCUMENT> labelMTS,
# FilterFunction<DOCUMENT> anchor, long leftDelta, long rightDelta, TERM[] keys, boolean withReplacement

def fit(data_mts, label_mts, anchor, left_delta, right_delta, keys, with_replacement):
    tsc = data_mts._tsc

    if hasattr(anchor, '__call__'):
        func = tsc.java_bridge.java_implementations.FilterFunction(anchor)
    else:
        func = tsc.packages.time_series.transforms.utils.python.Expressions.toFilterFunction(anchor)

    j_keys = tsc.java_bridge.convert_to_primitive_java_array(keys, str)

    j_tfidf = tsc.packages.time_series.ml.tfidf.TFIDF.fit(
        data_mts._j_mts,
        label_mts._j_mts,
        func,
        left_delta,
        right_delta,
        j_keys,
        with_replacement
    )

    from autoai_ts_libs.deps.tspy.data_structures.ml.TFIDF import TFIDF
    return TFIDF(tsc, j_tfidf)

