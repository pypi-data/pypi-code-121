from autoai_ts_libs.deps.tspy import _get_context

def linear(pre_cursors=1, post_cursors=1):
    tsc = _get_context()
    return tsc.packages.time_series.forecasting.transformation.interpolate\
        .OnlineLinearInterpolator(pre_cursors, post_cursors)

def spline(pre_cursors=3, post_cursors=3):
    tsc = _get_context()
    return tsc.packages.time_series.forecasting.transformation.interpolate \
        .OnlineSplineInterpolator(pre_cursors, post_cursors)

def average(pre_cursors, post_cursors):
    tsc = _get_context()
    return tsc.packages.time_series.forecasting.transformation.interpolate \
        .OnlineAveragingInterpolator(pre_cursors, post_cursors)

def forecast(model):
    tsc = _get_context()
    return tsc.packages.time_series.forecasting.transformation.interpolate \
        .OnlineForecastingInterpolator(model._j_fm)
