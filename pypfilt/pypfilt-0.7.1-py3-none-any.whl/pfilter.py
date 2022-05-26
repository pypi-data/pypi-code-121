"""Particle filter core: simulate time-steps and adjust particle weights."""

import logging
import numpy as np

from . import cache, resample
from . import obs as obs_mod
from . import state as state_mod


def reweight(ctx, snapshot, obs):
    """Adjust particle weights in response to some observation(s).

    :param ctx: The simulation parameters.
    :type ctx: ~pypfilt.build.Context
    :param snapshot: The current particle states.
    :type snapshot: ~pypfilt.state.Snapshot
    :param obs: The observation(s) that have been made.

    :returns: A tuple; the first element (*bool*) indicates whether resampling
        is required, the second element (*float*) is the **effective** number
        of particles (i.e., accounting for weights).
    """
    # Calculate the log-likelihood of obtaining the given observation, for
    # each particle.
    logs = obs_mod.log_llhd(ctx, snapshot, obs)

    # Scale the log-likelihoods so that the maximum is 0 (i.e., has a
    # likelihood of 1) to increase the chance of smaller likelihoods
    # being within the range of double-precision floating-point.
    logs = logs - np.max(logs)
    # Calculate the effective number of particles, prior to reweighting.
    prev_eff = 1.0 / sum(w * w for w in snapshot.weights)
    # Update the current weights.
    snapshot.weights *= np.exp(logs)
    ws_sum = np.sum(sorted(snapshot.weights))
    if ws_sum == 0:
        raise ValueError('Updated particle weights sum to zero')
    # Renormalise the weights.
    snapshot.weights /= ws_sum
    if np.any(np.isnan(snapshot.weights)):
        # Either the new weights were all zero, or every new non-zero weight
        # is associated with a particle whose previous weight was zero.
        nans = np.sum(np.isnan(snapshot.weights))
        raise ValueError("{} NaN weights; ws_sum = {}".format(nans, ws_sum))
    # Determine whether resampling is required.
    num_eff = 1.0 / sum(w * w for w in snapshot.weights)
    req_resample = (num_eff / ctx.settings['filter']['particles']
                    < ctx.settings['filter']['resample']['threshold'])

    # Detect when the effective number of particles has greatly decreased.
    eff_decr = num_eff / prev_eff
    if (eff_decr < 0.1):
        # Note: this could be mitigated by replacing the weights with their
        # square roots (for example) until the decrease is sufficiently small.
        logger = logging.getLogger(__name__)
        logger.debug("Effective particles decreased by {}".format(eff_decr))

    return (req_resample, num_eff)


def __log_step(ctx, when, do_resample, num_eff=None):
    """Log the state of the particle filter when an observation is made or
    when particles have been resampled.

    :param ctx: The simulation parameters.
    :type ctx: ~pypfilt.build.Context
    :param when: The current simulation time.
    :param do_resample: Whether particles were resampled at this time-step.
    :type do_resample: bool
    :param num_eff: The effective number of particles (default is ``None``).
    :type num_eff: float
    """
    logger = logging.getLogger(__name__)
    resp = {True: 'Y', False: 'N'}
    if num_eff is not None:
        logger.debug('{} RS: {}, #px: {:7.1f}'.format(
            ctx.component['time'].to_unicode(when), resp[do_resample],
            num_eff))
    elif do_resample:
        logger.debug('{} RS: {}'.format(
            ctx.component['time'].to_unicode(when), resp[do_resample]))


def step(ctx, snapshot, step_num, step_obs, is_fs):
    """Perform a single time-step for every particle.

    :param ctx: The simulation parameters.
    :type ctx: ~pypfilt.build.Context
    :param snapshot: The current particle states.
    :type snapshot: ~pypfilt.state.Snapshot
    :param step_num: The time-step number.
    :param step_obs: The list of observations for this time-step.
    :param is_fs: Indicate whether this is a forecasting simulation (i.e., no
        observations).
        For deterministic models it is useful to add some random noise when
        estimating, to allow identical particles to differ in their behaviour,
        but this is not desirable when forecasting.

    :return: ``True`` if resampling was performed, otherwise ``False``.
    """
    when = snapshot.time
    d_t = ctx.settings['time']['dt']

    # Define the particle ordering, which may be updated by ``resample``.
    # This must be defined before we can use `snapshot.back_n_steps()`.
    curr = snapshot.vec
    curr['prev_ix'] = np.arange(ctx.settings['filter']['particles'])
    prev = snapshot.back_n_steps(1)

    # Step each particle forward by one time-step.
    curr_sv = curr['state_vec']
    prev_sv = prev['state_vec']
    ctx.component['model'].update(ctx, when, d_t, is_fs, prev_sv, curr_sv)

    # Copy the particle weights from the previous time-step.
    # These will be updated by ``reweight`` as necessary.
    curr['weight'] = prev['weight']

    # Update sample lookup columns, if present.
    if curr.dtype.names is not None and 'lookup' in curr.dtype.names:
        curr['lookup'] = prev['lookup']

    # Account for observations, if any.
    num_eff = None
    do_resample = False
    if step_obs:
        do_resample, num_eff = reweight(ctx, snapshot, step_obs)

    __log_step(ctx, when, do_resample, num_eff)

    # Perform resampling when required.
    if do_resample:
        ctx.call_event_handlers('before_resample', ctx, when, curr)
        resample.resample(ctx, curr)
        __log_step(ctx, when, True, ctx.settings['filter']['particles'])
        ctx.call_event_handlers('after_resample', ctx, when, curr)

    # Indicate whether resampling occurred at this time-step.
    return do_resample


def run(ctx, start, end, obs_tables, history=None,
        save_when=None, save_to=None):
    """Run the particle filter against any number of data streams.

    :param ctx: The simulation parameters.
    :type ctx: ~pypfilt.build.Context
    :param start: The start of the simulation period.
    :param end: The (**exclusive**) end of the simulation period.
    :param obs_tables: A dictionary of observation tables.
    :param history: The (optional) history matrix state from which to resume.
    :param save_when: Times at which to save the particle history matrix.
    :param save_to: The filename for saving the particle history matrix.

    :returns: The resulting simulation state: a dictionary that contains the
        simulation settings (``'settings'``), the particle history matrix
        (``'history'``), and the summary statistics (``'summary'``).
    """
    # Record the start and end of this simulation.
    ctx.settings['time']['sim_start'] = start
    ctx.settings['time']['sim_until'] = end

    sim_time = ctx.component['time']
    sim_time.set_period(
        start, end, ctx.settings['time']['steps_per_unit'])
    steps = sim_time.with_observation_tables(ctx, obs_tables)

    # Determine whether this is a forecasting run, by checking whether there
    # are any observation tables.
    is_fs = not obs_tables

    # Create the history component and store it in the simulation context.
    # We allow the history matrix to be provided in order to allow, e.g., for
    # forecasting from any point in a completed simulation.
    if history is None:
        history = state_mod.History(ctx)
    ctx.component['history'] = history

    # Allocate space for the summary statistics.
    summary = ctx.component['summary']
    summary.allocate(ctx, forecasting=is_fs)

    # Define key time-step loop variables.
    # The start of the next interval that should be summarised.
    win_start = start
    # The time of the previous time-step (if any).
    most_recent = None

    # Simulate each time-step.
    # NOTE: the first time-step is number 1 and updates history.matrix[1] from
    # history.matrix[0].
    for (step_num, when, obs) in steps:
        history.set_time_step(step_num, when)
        # Check whether the end of the history matrix has been reached.
        # If so, shift the sliding window forward in time.
        if history.reached_window_end():
            # Calculate summary statistics in blocks.
            # If most_recent is None, no time-steps have been simulated.
            # This can occur when (for example) a forecasting simulation has
            # started at the final time-step in the history matrix.
            # The correct response is to only calculate summary statistics for
            # this single time-step.
            win_end = win_start if most_recent is None else most_recent
            window = history.summary_window(ctx, win_start, win_end)
            summary.summarise(ctx, window)

            # NOTE: win_start is the start of the next interval that will be
            # summarised. Since the current time-step is not evaluated until
            # after the above call to summary.summarise(), the next summary
            # window should start at this time-step.
            win_start = when

            # Shift the moving window so that we can continue the simulation.
            shift = (ctx.settings['filter']['history_window']
                     * ctx.settings['time']['steps_per_unit'])
            history.shift_window_back(shift)

        # Simulate the current time-step.
        snapshot = history.snapshot(ctx, when)
        resampled = step(ctx, snapshot, step_num, obs, is_fs)
        # Record whether the particles were resampled at this time-step.
        history.set_resampled(resampled)

        # Check whether to save the particle history matrix to disk.
        # NOTE: the summary object may not have summarised the model state
        # recently, or even at all if we haven't reached the end of the
        # sliding window at least once.
        if save_when is not None and save_to is not None:
            if when in save_when:
                # First, summarise up to the previous time-step.
                # NOTE: we do not want to summarise the current time-step,
                # because simulations that resume from this saved state will
                # begin summarising from their initial state, which is this
                # current time-step. So if the summary window starts at the
                # current time-step, we should not summarise before saving.
                if win_start < when:
                    win_end = win_start if most_recent is None else most_recent
                    window = history.summary_window(ctx, win_start, win_end)
                    summary.summarise(ctx, window)

                # Update the start of the next summary interval.
                win_start = when

                # Note: we only need to save the current matrix block!
                cache.save_state(save_to, ctx, when)

        # Finally, update loop variables.
        most_recent = when

    if history.index is None:
        # There were no time-steps, so return nothing.
        return None

    # Calculate summary statistics for the remaining time-steps.
    if most_recent is not None:
        window = history.summary_window(ctx, win_start, most_recent)
        summary.summarise(ctx, window)

    # Return the complete simulation state.
    return {'settings': ctx.settings,
            'history': history,
            'summary': summary.get_stats()}
