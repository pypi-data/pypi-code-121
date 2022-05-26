"""Simulation time scales and units."""

import abc
import datetime
import math
import numpy as np


class Time(abc.ABC):
    """
    The base class for simulation time scales, which defines the minimal set
    of methods that are required.
    """

    def __init__(self):
        """
        Return a time scale with no defined simulation period.
        """
        self._start = None
        self._end = None
        self.steps_per_unit = None

    def set_period(self, start, end, steps_per_unit):
        """
        Define the simulation period and time-step size.

        :param start: The start of the simulation period.
        :param end: The end of the simulation period.
        :param steps_per_unit: The number of time-steps per time unit.
        :type steps_per_unit: int
        :raises ValueError: if ``steps_per_unit`` is not a positive integer.
        """
        if not isinstance(steps_per_unit, int) or steps_per_unit < 1:
            msg = "Invalid steps_per_unit: {}".format(steps_per_unit)
            raise ValueError(msg)
        self._start = start
        self._end = end
        self.steps_per_unit = steps_per_unit

    @abc.abstractmethod
    def dtype(self, name):
        """
        Define the dtype for columns that store times.
        """
        pass

    @abc.abstractmethod
    def native_dtype(self):
        """
        Define the Python type used to represent times in NumPy arrays.
        """
        pass

    @abc.abstractmethod
    def is_instance(self, value):
        """
        Return whether ``value`` is an instance of the native time type.
        """
        pass

    @abc.abstractmethod
    def to_dtype(self, time):
        """
        Convert from time to a dtype value.
        """
        pass

    @abc.abstractmethod
    def from_dtype(self, dval):
        """
        Convert from a dtype value to time.
        """
        pass

    @abc.abstractmethod
    def to_unicode(self, time):
        """
        Convert from time to a Unicode string.

        This is used to define group names in HDF5 files, and for logging.
        """
        pass

    @abc.abstractmethod
    def from_unicode(self, val):
        """
        Convert from a Unicode string to time.

        This is used to parse group names in HDF5 files.
        """
        pass

    @abc.abstractmethod
    def column(self, name):
        """
        Return a tuple that can be used with :func:`~pypfilt.io.read_table` to
        convert a column into time values.
        """
        pass

    @abc.abstractmethod
    def steps(self):
        """
        Return a generator that yields a sequence of time-step numbers and
        times (represented as tuples) that span the simulation period.

        The first time-step should be numbered 1 and occur at a time that is
        one time-step after the beginning of the simulation period.
        """
        pass

    @abc.abstractmethod
    def step_count(self):
        """
        Return the number of time-steps required for the simulation period.
        """
        pass

    @abc.abstractmethod
    def step_of(self, time):
        """
        Return the time-step number that corresponds to the specified time.
        """
        pass

    @abc.abstractmethod
    def add_scalar(self, time, scalar):
        """
        Add a scalar quantity to the specified time.
        """
        pass

    @abc.abstractmethod
    def time_of_obs(self, obs):
        """
        Return the time associated with an observation.
        """
        pass

    def to_scalar(self, time):
        """
        Convert the specified time into a scalar quantity, defined as the
        time-step number divided by the number of time-steps per time unit.
        """
        return self.step_of(time) / self.steps_per_unit

    def with_observation_tables(self, ctx, obs_tables):
        """
        Return a generator that yields a sequence of tuples that contain: the
        time-step number, the current time, and a list of observations.

        :param ctx: The simulation context.
        :type ctx: pypfilt.Context
        :param obs_tables: The observation data tables.
        :type obs_tables: Dict[str, numpy.ndarray]
        """
        items = self.with_observation_tables_from_time(ctx, obs_tables, None)
        for x in items:
            yield x

    def with_observation_tables_from_time(self, ctx, obs_tables, start):
        """
        Return a generator that yields a sequence of tuples that contain: the
        time-step number, the current time, and a list of observations.

        :param ctx: The simulation context.
        :type ctx: pypfilt.Context
        :param obs_tables: The observation data tables.
        :type obs_tables: Dict[str, numpy.ndarray]
        :param start: The starting time (set to ``None`` to use the start of
            the simulation period).
        """
        if start is None:
            start = self._start

        # For each observations table, record the row index and observation
        # dictionary of the next observation.
        obs_streams = {}
        for (obs_unit, obs_data) in obs_tables.items():
            obs_model = ctx.component['obs'][obs_unit]
            (row_ix, obs) = find_first_observation_after(
                obs_model, obs_data, start)
            if row_ix is None or obs is None:
                continue
            obs_streams[obs_unit] = (row_ix, obs)

        for (step, t) in self.steps():
            # Skip to the first time-step *after* the starting time.
            if t <= start:
                continue

            # Find all observations that pertain to this time-step.
            curr_obs = []
            update_units = []
            for (obs_unit, (row_ix, obs)) in obs_streams.items():
                if obs['date'] > t:
                    continue
                curr_obs.append(obs)
                update_units.append(obs_unit)

            # Remove observations for this time-step from obs_streams.
            if len(update_units) > 0:
                for obs_unit in update_units:
                    # NOTE: must retrieve the correct observation model and
                    # data table.
                    obs_model = ctx.component['obs'][obs_unit]
                    obs_data = obs_tables[obs_unit]
                    (row_ix, _) = obs_streams[obs_unit]
                    (new_ix, obs) = find_first_observation_after(
                        obs_model, obs_data, start, first_ix=row_ix + 1)
                    if new_ix is None or obs is None:
                        del obs_streams[obs_unit]
                    else:
                        obs_streams[obs_unit] = (new_ix, obs)

            # Yield a (step_number, time, observations) tuple.
            yield (step, t, curr_obs)


def find_first_observation_after(obs_model, obs_data, start, first_ix=0):
    """
    Return the row index and observation dictionary for the first observation
    in ``obs_data`` that occurs **after** the time ``start``.
    If no such observation exists, return ``(None, None)``.

    :param obs_model: The observation model for these observations.
    :type obs_model: pypfilt.Obs
    :param obs_data: The observations table.
    :type obs_data: numpy.ndarray
    :param start: The time after which the next observation should occur.
    :param first_ix: The row index from which to begin searching.
    :type first_ix: int
    """
    row_ixs = range(first_ix, len(obs_data))
    for ix in row_ixs:
        row = obs_data[ix]
        obs = obs_model.row_into_obs(row)

        if obs['date'] > start:
            return (ix, obs)

    return (None, None)


class Datetime(Time):
    """
    A ``datetime`` scale where the time unit is days.
    """

    def __init__(self, fmt=None, date_fmt=None):
        """
        :param fmt: The format string used to serialise ``datetime`` objects;
            the default is ``'%Y-%m-%d %H:%M:%S'``.
        :param date_fmt: The format string used to read ``date`` objects; the
            default is ``'%Y-%m-%d'``.
        """
        super(Datetime, self).__init__()
        if fmt is None:
            fmt = '%Y-%m-%d %H:%M:%S'
        self.fmt = fmt
        if date_fmt is None:
            date_fmt = '%Y-%m-%d'
        self.date_fmt = date_fmt

    def set_period(self, start, end, steps_per_unit):
        """
        Define the simulation period and time-step size.

        :param start: The start of the simulation period.
        :type start: datetime.datetime
        :param end: The end of the simulation period.
        :type end: datetime.datetime
        :param steps_per_unit: The number of time-steps per day.
        :type steps_per_unit: int
        :raises ValueError: if ``start`` and/or ``end`` are not
            ``datetime.datetime`` instances, or if ``steps_per_unit`` is not a
            positive integer.
        """
        # Ensure that start and end are both datetime instances.
        if not isinstance(start, datetime.datetime):
            raise ValueError("Invalid start: {}".format(start))
        if not isinstance(end, datetime.datetime):
            raise ValueError("Invalid end: {}".format(end))
        super(Datetime, self).set_period(start, end, steps_per_unit)

    def dtype(self, name):
        """Define the dtype for columns that store times."""
        # NOTE: np.issubdtype doesn't consider string lengths.
        return (name, np.dtype('S20'))

    def native_dtype(self):
        """Define the Python type used to represent times in NumPy arrays."""
        return 'O'

    def is_instance(self, value):
        """Return whether ``value`` is an instance of the native time type."""
        return isinstance(value, datetime.datetime)

    def to_dtype(self, time):
        """Convert from time to a dtype value."""
        return time.strftime(self.fmt).encode('utf-8')

    def from_dtype(self, dval):
        """Convert from a dtype value to time."""
        if isinstance(dval, bytes):
            dval = dval.decode('utf-8')
        try:
            return datetime.datetime.strptime(dval, self.fmt)
        except ValueError:
            return datetime.datetime.strptime(dval, self.date_fmt)

    def to_unicode(self, time):
        """Convert from time to a Unicode string."""
        return time.strftime(self.fmt)

    def from_unicode(self, val):
        """Convert from a Unicode string to time."""
        return self.from_dtype(val)

    def column(self, name):
        """
        Return a tuple that can be used with :func:`~pypfilt.io.read_table` to
        convert a column into time values.
        """
        return (name, 'O', self.from_dtype)

    def steps(self):
        """
        Return a generator that yields a sequence of time-step numbers and
        times (represented as tuples) that span the simulation period.

        The first time-step should be numbered 1 and occur at a time that is
        one time-step after the beginning of the simulation period.
        """
        delta = datetime.timedelta(days=1.0 / self.steps_per_unit)
        one_day = datetime.timedelta(days=1)

        step = 1
        time = self._start + delta
        while time <= self._end:
            yield (step, time)
            # Proceed to the next time-step.
            step += 1
            curr_day = step // self.steps_per_unit
            curr_off = step % self.steps_per_unit
            time = self._start + curr_day * one_day + curr_off * delta

    def step_count(self):
        """
        Return the number of time-steps required for the simulation period.
        """
        return self.step_of(self._end)

    def step_of(self, time):
        """
        Return the time-step number that corresponds to the specified time.

        - For ``date`` objects, the time-step number marks the **start of that
          day**.
        - For ``datetime`` objects, the time-step number is rounded to the
          **nearest** time-step.
        - For all other values, this will raise ``ValueError``.
        """
        if not isinstance(time, datetime.datetime):
            if isinstance(time, datetime.date):
                time = datetime.datetime(time.year, time.month, time.day)

        if isinstance(time, datetime.datetime):
            diff = time - self._start
            frac_diff = diff - datetime.timedelta(diff.days)
            frac_day = frac_diff.total_seconds()
            frac_day /= datetime.timedelta(days=1).total_seconds()
            day_steps = diff.days * self.steps_per_unit
            day_frac = frac_day * float(self.steps_per_unit)
            return day_steps + round(day_frac)
        else:
            raise ValueError("{}.step_of() does not understand {}".format(
                type(self).__name__, type(time)))

    def add_scalar(self, time, scalar):
        """Add a scalar quantity to the specified time."""
        return time + datetime.timedelta(scalar)

    def time_of_obs(self, obs):
        """
        Return the time associated with an observation.
        """
        d = obs['date']
        if isinstance(d, datetime.datetime):
            return d
        else:
            raise ValueError("{}.{}() does not understand {}".format(
                type(self).__name__, "time_of_obs", type(d)))


class Scalar(Time):
    """
    A dimensionless time scale.
    """

    def __init__(self, np_dtype=None):
        """
        :param np_dtype: The data type used for serialisation; the default is
            ``np.float64``.
        """
        super(Scalar, self).__init__()
        if np_dtype is None:
            np_dtype = np.float64
        self.np_dtype = np_dtype

    def set_period(self, start, end, steps_per_unit):
        """
        Define the simulation period and time-step size.

        :param start: The start of the simulation period.
        :type start: float
        :param end: The end of the simulation period.
        :type end: float
        :param steps_per_unit: The number of time-steps per day.
        :type steps_per_unit: int
        :raises ValueError: if ``start`` and/or ``end`` are not floats, or if
            ``steps_per_unit`` is not a positive integer.
        """
        # Note: if start or end are not floats, we shouldn't try converting
        # them to floats because they are used to determine HDF5 group names
        # and so their string representation is (unfortunately) important.
        if not isinstance(start, (float, self.np_dtype)):
            raise ValueError("invalid start type: {}".format(type(start)))
        if not isinstance(end, (float, self.np_dtype)):
            raise ValueError("invalid end type: {}".format(type(start)))
        super(Scalar, self).set_period(start, end, steps_per_unit)

    def dtype(self, name):
        """Define the dtype for columns that store times."""
        return (name, self.np_dtype)

    def native_dtype(self):
        """Define the Python type used to represent times in NumPy arrays."""
        return self.np_dtype

    def is_instance(self, value):
        """Return whether ``value`` is an instance of the native time type."""
        return isinstance(value, (float, self.np_dtype))

    def to_dtype(self, time):
        """Convert from time to a dtype value."""
        return self.np_dtype(time)

    def from_dtype(self, dval):
        """Convert from a dtype value to time."""
        if isinstance(dval, np.ndarray):
            return dval.item()
        else:
            return self.np_dtype(dval)

    def to_unicode(self, time):
        """Convert from time to a Unicode string."""
        return str(time)

    def from_unicode(self, val):
        """Convert from a Unicode string to time."""
        return float(val)

    def column(self, name):
        """
        Return a tuple that can be used with :func:`~pypfilt.io.read_table` to
        convert a column into time values.
        """
        return (name, self.np_dtype)

    def steps(self):
        """
        Return a generator that yields a sequence of time-step numbers and
        times (represented as tuples) that span the simulation period.

        The first time-step should be numbered 1 and occur at a time that is
        one time-step after the beginning of the simulation period.
        """
        delta = 1 / self.steps_per_unit
        time = self._start + delta
        step = 1
        while time <= self._end:
            yield (step, time)
            # Proceed to the next time-step.
            step += 1
            curr_units = step // self.steps_per_unit
            curr_rems = step % self.steps_per_unit
            time = self._start + curr_units + curr_rems * delta

    def step_count(self):
        """
        Return the number of time-steps required for the simulation period.
        """
        return self.step_of(self._end)

    def step_of(self, time):
        """
        Return the time-step number that corresponds to the specified time.
        Fractional values are rounded to the **nearest** time-step.
        """
        frac, whole = math.modf(time - self._start)
        frac_steps = round(frac * self.steps_per_unit)
        whole = int(whole)
        return (whole * self.steps_per_unit) + frac_steps

    def add_scalar(self, time, scalar):
        """Add a scalar quantity to the specified time."""
        return time + scalar

    def time_of_obs(self, obs):
        """
        Return the time associated with an observation.
        """
        return obs['date']
