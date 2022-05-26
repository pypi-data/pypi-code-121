"""Base class for simulation models."""

import abc
import copy
import functools
import numpy as np


class Model(abc.ABC):
    """
    The base class for simulation models, which defines the minimal set of
    methods that are required.
    """

    @abc.abstractmethod
    def init(self, ctx, vec):
        """
        Initialise a matrix of state vectors.

        :param ctx: The simulation context.
        :param vec: An uninitialised :math:`P \\times S` matrix of state
            vectors, for :math:`P` particles and state vectors of length
            :math:`S` (as defined by :py:func:`~field_types`).
        """
        pass

    @abc.abstractmethod
    def field_types(self, ctx):
        """
        Return a list of ``(field_name, field_dtype, field_shape)`` tuples
        that define the state vector.

        The third element, ``field_shape``, is optional and contains the shape
        of this field if it forms an array of type ``field_dtype``.

        These tuples **must** be in the same order as the state vector itself.

        :param ctx: The simulation context.
        """
        pass

    def field_names(self, ctx):
        """
        Return a list of the fields that define the state vector.

        These tuples **must** be in the same order as the state vector itself.

        :param ctx: The simulation context.
        """
        return [field[0] for field in self.field_types(ctx)]

    @abc.abstractmethod
    def can_smooth(self):
        """
        Return the set of field names in the state vector that can be smoothed
        by the post-regularised particle filter (see
        :func:`~pypfilt.resample.post_regularise`).
        """
        pass

    @abc.abstractmethod
    def update(self, ctx, time, dt, is_fs, prev, curr):
        """
        Perform a single time-step, jumping forward to ``time`` and recording
        the updated particle states in ``curr``.

        :param ctx: The simulation context.
        :param time: The (end) time of the current time-step.
        :param dt: The time-step size.
        :param is_fs: Indicates whether this is a forecasting simulation.
        :param prev: The state before the time-step.
        :param curr: The state after the time-step (destructively updated).
        """
        pass

    def resume_from_cache(self, ctx):
        """
        Notify the model that a simulation will begin from a saved state.

        The model does not need to initialise the state vectors, since these
        will have been loaded from a cache file, but it may need to update any
        internal variables (i.e., those not stored in the state vectors).

        .. note:: Models should only implement this method if they need to
           prepare for the simulation.
        """
        pass

    def stat_info(self):
        """
        Describe each statistic that can be calculated by this model as a
        ``(name, stat_fn)`` tuple, where ``name`` is a string that identifies
        the statistic and ``stat_fn`` is a function that calculates the value
        of the statistic.

        .. note:: Models should only implement this method if they define one
           or more statistics.
        """
        return []

    def is_valid(self, hist):
        """
        Identify particles whose state and parameters can be inspected. By
        default, this function returns ``True`` for all particles. Override
        this function to ensure that inchoate particles are correctly
        ignored.

        .. note:: Models should only implement this method if there are
           conditions where some particles should be ignored.
        """
        return np.ones(hist.shape, dtype=bool)


def ministeps(mini_steps=None):
    """
    Wrap a model's ``update()`` method to perform multiple "mini-steps" for
    each time-step.

    :param mini_steps: The (optional) number of "mini-steps" to perform for
        each time-step.
        This can be overridden by providing a value for the
        ``"time.mini_steps_per_step"`` setting.
    """
    def decorator(update_method):
        num_setting = ['time', 'mini_steps_per_step']
        setting_name = '.'.join(num_setting)

        @functools.wraps(update_method)
        def wrapper(self, ctx, time, dt, is_fs, prev, curr):
            # Determine the number of mini-steps to perform.
            mini_num = ctx.get_setting(num_setting, mini_steps)
            if mini_num is None:
                msg_fmt = 'Must define setting "{}"'
                raise ValueError(msg_fmt.format(setting_name))

            # Performing one mini-step per time-step is simple.
            if mini_num == 1:
                update_method(self, ctx, time, dt, is_fs, prev, curr)
                return

            # Define the simulation period and time-step size.
            full_scale = ctx.component['time']
            mini_scale = copy.copy(full_scale)
            prev_time = full_scale.add_scalar(time, -dt)
            mini_per_unit = mini_num * ctx.settings['time']['steps_per_unit']
            mini_scale.set_period(prev_time, time, mini_per_unit)

            # Create temporary arrays for the previous and current state.
            mini_prev = prev.copy()
            mini_curr = curr.copy()

            # Note that we need to substitute the time scale component.
            # This ensures that if the model uses any time methods, such as
            # to_scalar(), it will be consistent with the mini-step scale.
            ctx.component['time'] = mini_scale
            # Simulate each mini-step.
            mini_dt = dt / mini_num
            for (mini_step_num, mini_time) in mini_scale.steps():
                update_method(self, ctx, mini_time, mini_dt, is_fs,
                              mini_prev, mini_curr)
                mini_prev, mini_curr = mini_curr, mini_prev
            # Restore the original time scale component.
            ctx.component['time'] = full_scale

            # Update the output state vectors.
            # NOTE: the final state is recorded in mini_prev, because we
            # switch mini_prev and mini_curr after each mini-step.
            curr[:] = mini_prev[:]

        return wrapper

    return decorator
