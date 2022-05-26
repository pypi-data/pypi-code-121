from dataclasses import dataclass
from shyft.time_series import (Calendar, UtcPeriod, time, TimeAxis, min_utctime, max_utctime, UtcTimeVector,
                               time_axis_extract_time_points_as_utctime, TimeAxisType)


def create_view_time_axis(*, cal: Calendar, view_period: UtcPeriod, clip_period: UtcPeriod, dt: time) -> TimeAxis:
    """ Creates a time axis with the range of the view_period, that snaps to the calendar resolution of dt.

    An *empty* TimeAxis() is returned if:
     - no overlap
     - overlap period contains -oo or +oo
     - dt is zero

    Parameters
    ----------
    cal: Calendar to use for calendar semantic trim/add if dt >= DAY
    view_period: the visual view-period
    clip_period: if a valid clip_period is specified, the time axis will clipped to this period
    dt: time step of the time axis

    Returns
    -------
    time_axis: TimeAxis. Axis type is Fixed if dt < DAY (optimization), else Calendar.
    """
    overlap = UtcPeriod.intersection(view_period, clip_period) if clip_period.valid() else view_period

    if (dt <= 0 or not overlap.valid() or overlap.start == min_utctime or overlap.end == max_utctime):
        return TimeAxis()

    if overlap.timespan() < dt:
        t_start = cal.trim(overlap.start, dt)
        n = 1
        return TimeAxis(cal, t_start, dt, n)

    t_start = cal.trim(overlap.start + dt/2, dt)  # the + dt/2.0 ensure calendar rounding, as opposed to trunc/trim
    n = UtcPeriod(t_start, cal.trim(overlap.end + dt/2, dt)).diff_units(cal, dt)
    return TimeAxis(cal, t_start, dt, n)


def period_union(p1: UtcPeriod, p2: UtcPeriod) -> UtcPeriod:
    if p1.valid() and p2.valid():
        pass
    else:
        raise ValueError("Union cannot be formed with no-valid periods.")

    if UtcPeriod.intersection(p1, p2).valid():
        start = min(p1.start, p2.start)
        end = max(p1.end, p2.end)
        return UtcPeriod(start, end)
    else:
        raise NotImplementedError("union not implemented for non-overlapping UtcPeriods.")


class ViewTimeAxisProperties:
    """
    At the view-level, describes the visual-wanted properties of the time-series data to be presented.
    The class have no logic, just group together properties that give a consistent view of current 'view-port'.

    The data-source can use this information to adapt it's call to the underlying TsAdapter(time-axis,unit)->tsvector
    so that it is optimal with respect to performance, as well as visualization.

    Attributes
    ----------
    dt: time-step for aggregation/average, like hour, day, week etc.
    cal: calendar for calendar semantic steps, so the time-steps dt are in multiple of dt, rounded to calendar
    view_period: the current entire view-period (usually also rounded to whole calendar/dt)
    padded_view_period: a period greater/equal to the view-period, to allow for smooth pan/scrolling
    extend_mode: if True, the data-source should ensure to include its own min/max range using the extend_time_axis method
    """

    def __init__(self, *, dt: time, cal: Calendar, view_period: UtcPeriod, padded_view_period: UtcPeriod, extend_mode:bool):
        self.dt: time = dt
        self.cal: Calendar = cal
        self.view_period: UtcPeriod = view_period
        self.padded_view_period: UtcPeriod = padded_view_period
        self.extend_mode:bool = extend_mode
