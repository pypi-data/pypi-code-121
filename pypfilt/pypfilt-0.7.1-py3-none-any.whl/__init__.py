"""A bootstrap particle filter for epidemic forecasting."""

import datetime
import logging
import os
import os.path

from . import cache
from . import build
from . import pfilter
from . import io
from . import model
from . import obs
from . import sampler
from . import scenario
from . import summary
from . import time
from . import version

__package_name__ = u'pypfilt'
__author__ = u'Rob Moss'
__email__ = u'rgmoss@unimelb.edu.au'
__copyright__ = u'2014-2022, Rob Moss'
__license__ = u'BSD 3-Clause License'
__version__ = version.__version__


# Export abstract base classes from this module.
Instance = scenario.Instance
Context = build.Context
Obs = obs.Obs
Model = model.Model
Monitor = summary.Monitor
Table = summary.Table
Datetime = time.Datetime
Scalar = time.Scalar

load_instances = scenario.load_instances

# Prevent an error message if the application does not configure logging.
log = logging.getLogger(__name__).addHandler(logging.NullHandler())


def simulate_from_model(instance, particles=1, common_prng_seed=False):
    """
    Simulate observations from a model.

    :param instance: The scenario instance.
    :type instance: pypfilt.scenario.Instance
    :param particles: The number of particles; set this to ``None`` to use the
        number of particles defined in ``instance``.
    :param common_prng_seed: Whether the simulated observation tables should
        use a common PRNG seed to generate the simulated observations.
    :return: A dictionary of simulated observation tables.
    :rtype: Dict[str, numpy.ndarray]

    .. note:: The ``instance`` **should not be reused** after calling this
        function.
        To prevent this from happening, the instance settings will be deleted.

    :Examples:

    >>> import pypfilt
    >>> import pypfilt.examples.predation
    >>> pypfilt.examples.predation.write_example_files()
    >>> config_file = 'predation.toml'
    >>> for instance in pypfilt.load_instances(config_file):
    ...     obs_tables = pypfilt.simulate_from_model(instance, particles=1)
    ...     # Print the first four simulated 'x' observations.
    ...     x_obs = obs_tables['x']
    ...     print(x_obs[['date', 'value']][:4])
    ...     # Print the first four simulated 'y' observations.
    ...     y_obs = obs_tables['y']
    ...     print(y_obs[['date', 'value']][:4])
    [(0., 1.35192613) (1., 1.54456968) (2., 1.92089402) (3., 1.21987828)]
    [(0., -0.14294339) (1.,  0.51293146) (2.,  1.1426979 ) (3.,  0.83975596)]
    >>> print(instance.settings)
    {}
    """
    logger = logging.getLogger(__name__)

    if not isinstance(instance, scenario.Instance):
        msg_fmt = 'Value of type {} is not a scenario instance'
        raise ValueError(msg_fmt.format(type(instance)))

    # NOTE: only overwrite/replace summary tables and monitors.
    # Leave other summary settings untouched.
    if 'tables' in instance.settings['summary']:
        del instance.settings['summary']['tables']
    if 'monitors' in instance.settings['summary']:
        del instance.settings['summary']['monitors']
    # NOTE: remove initialisation arguments for custom summary components.
    if 'init' in instance.settings['summary']:
        del instance.settings['summary']['init']

    instance.settings['summary']['tables'] = {}

    # NOTE: we need a separate table for each observation unit.
    obs_units = instance.settings.get('observations', {}).keys()
    for obs_unit in obs_units:
        instance.settings['summary']['tables'][obs_unit] = {
            'component': 'pypfilt.summary.SimulatedObs',
            'observation_unit': obs_unit,
            'common_prng_seed': common_prng_seed,
        }

    if particles is not None:
        instance.settings['filter']['particles'] = particles

    # To ensure that the simulation runs successfully, we have to avoid using
    # a custom summary function (such as epifx.summary.make), since they may
    # create tables that, e.g., require observations.
    instance.settings['components']['summary'] = 'pypfilt.summary.HDF5'

    # Do not load observations from disk.
    ctx = instance.build_context(obs_tables={})

    # Ensure that the output directory exists, or create it.
    io.ensure_directory_exists(ctx.settings['files']['output_directory'])

    ctx.component['summary'].initialise(ctx)

    # Empty instance.settings so that the instance cannot be reused.
    settings_keys = list(instance.settings.keys())
    for key in settings_keys:
        del instance.settings[key]

    start = ctx.settings['time']['start']
    until = ctx.settings['time']['until']
    logger.info("  {}  Estimating  from {} to {}".format(
        datetime.datetime.now().strftime("%H:%M:%S"),
        start, until))
    state = pfilter.run(ctx, start, until, {})

    # Return the dictionary of simulated observation tables.
    return state['summary']


def forecast(ctx, dates, filename):
    """Generate forecasts from various dates during a simulation.

    :param ctx: The simulation context.
    :type ctx: pypfilt.build.Context
    :param dates: The dates at which forecasts should be generated.
    :param filename: The output file to generate (can be ``None``).

    :returns: The simulation state for each forecast date.

    :Examples:

    >>> from datetime import datetime
    >>> import pypfilt
    >>> import pypfilt.build
    >>> import pypfilt.examples.predation
    >>> pypfilt.examples.predation.write_example_files()
    >>> config_file = 'predation-datetime.toml'
    >>> fs_dates = [datetime(2017, 5, 5), datetime(2017, 5, 10)]
    >>> data_file = 'output.hdf5'
    >>> for instance in pypfilt.load_instances(config_file):
    ...     context = instance.build_context()
    ...     state = pypfilt.forecast(context, fs_dates, filename=data_file)
    """

    if not isinstance(ctx, Context):
        msg_fmt = 'Value of type {} is not a simulation context'
        raise ValueError(msg_fmt.format(type(ctx)))

    # Ensure that there is at least one forecasting date.
    if len(dates) < 1:
        raise ValueError("No forecasting dates specified")

    start = ctx.settings['time']['start']
    end = ctx.settings['time']['until']
    if start is None or end is None:
        raise ValueError("Simulation period is not defined")

    # Ensure that the forecasting dates lie within the simulation period.
    invalid_fs = [ctx.component['time'].to_unicode(d) for d in dates
                  if d < start or d >= end]
    if invalid_fs:
        raise ValueError("Invalid forecasting date(s) {}".format(invalid_fs))

    logger = logging.getLogger(__name__)

    # Ensure that the output directory exists, or create it.
    io.ensure_directory_exists(ctx.settings['files']['output_directory'])

    # Initialise the summary object.
    ctx.component['summary'].initialise(ctx)

    # Generate forecasts in order from earliest to latest forecasting date.
    # Note that forecasting from the start date will duplicate the estimation
    # run (below) and is therefore redundant *if* sim['end'] is None.
    forecast_dates = [d for d in sorted(dates) if d >= start]

    # Identify the cache file, and remove it if instructed to do so.
    sim = cache.default(ctx, forecast_dates)
    cache_file = sim['save_to']
    if ctx.settings['files']['delete_cache_file_before_forecast']:
        cache.remove_cache_file(cache_file)

    # Load the most recently cached simulation state that is consistent with
    # the current observations.
    update = cache.load_state(cache_file, ctx, forecast_dates)
    if update is not None:
        for (key, value) in update.items():
            sim[key] = value

    # Update the forecasting dates.
    if not sim['fs_dates']:
        logger.warning("All {} forecasting dates precede cached state".format(
            len(forecast_dates)))
        return
    forecast_dates = sim['fs_dates']

    # Update the simulation period.
    if sim['start'] is not None:
        start = sim['start']
    if sim['end'] is not None:
        # Only simulate as far as the final forecasting date, then forecast.
        # Note that this behaviour may not always be desirable, so it can be
        # disabled by setting 'minimal_estimation_run' to False.
        if ctx.settings['filter']['minimal_estimation_run']:
            est_end = sim['end']
    else:
        est_end = end

    # Avoid the estimation pass when possible.
    state = None
    if start < est_end:
        logger.info("  {}  Estimating  from {} to {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"), start, est_end))
        state = pfilter.run(ctx, start, est_end, ctx.data['obs'],
                            history=sim['history'],
                            save_when=forecast_dates, save_to=sim['save_to'])
    else:
        logger.info("  {}  No estimation pass needed for {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"), est_end))

    if state is None:
        # NOTE: run() may return None if est_end < (start + dt).
        state = sim
        forecasts = {}
    else:
        # Save outputs from the estimation pass.
        # NOTE: record whether this simulation resumed from a cached state.
        if sim['start'] is not None:
            state['loaded_from_cache'] = sim['start']
        forecasts = {'complete': state}

    # Ensure the dates are ordered from latest to earliest.
    for start_date in forecast_dates:
        # We can reuse the history matrix for each forecast, since all of the
        # pertinent details are recorded in the summary.
        update = cache.load_state_at_time(cache_file, ctx, start_date)
        if update is None:
            msg = 'Cache file missing entry for forecast date {}'
            raise ValueError(msg.format(start_date))

        # The forecast may not extend to the end of the simulation period.
        fs_end = end
        if 'max_forecast_ahead' in ctx.settings['time']:
            max_end = ctx.component['time'].add_scalar(
                start_date,
                ctx.settings['time']['max_forecast_ahead'])
            if max_end < fs_end:
                fs_end = max_end

        logger.info("  {}  Forecasting from {} to {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"),
            ctx.component['time'].to_unicode(start_date),
            ctx.component['time'].to_unicode(fs_end)))

        fstate = pfilter.run(ctx, start_date, fs_end, {},
                             history=update['history'])
        fstate['loaded_from_cache'] = start_date

        forecasts[start_date] = fstate

    # Save the observations (flattened into a single list).
    forecasts['obs'] = ctx.all_observations

    # Save the forecasting results to disk.
    if filename is not None:
        logger.info("  {}  Saving to:  {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"), filename))
        # Save the results in the output directory.
        filepath = os.path.join(
            ctx.settings['files']['output_directory'], filename)
        ctx.component['summary'].save_forecasts(ctx, forecasts, filepath)

    # Remove the temporary file and directory.
    sim['clean']()

    # Remove the cache file if instructed to do so.
    if ctx.settings['files']['delete_cache_file_after_forecast']:
        cache.remove_cache_file(cache_file)

    return forecasts


def fit(ctx, filename):
    """
    Run a single estimation pass over the entire simulation period.

    :param ctx: The simulation context.
    :type ctx: pypfilt.build.Context
    :param filename: The output file to generate (can be ``None``).

    :returns: The simulation state for the estimation pass.

    :Examples:

    >>> import pypfilt
    >>> import pypfilt.build
    >>> import pypfilt.examples.predation
    >>> pypfilt.examples.predation.write_example_files()
    >>> config_file = 'predation.toml'
    >>> data_file = 'output.hdf5'
    >>> for instance in pypfilt.load_instances(config_file):
    ...     context = instance.build_context()
    ...     state = pypfilt.fit(context, filename=data_file)
    """
    if not isinstance(ctx, Context):
        msg_fmt = 'Value of type {} is not a simulation context'
        raise ValueError(msg_fmt.format(type(ctx)))

    start = ctx.settings['time']['start']
    until = ctx.settings['time']['until']
    if start is None or until is None:
        raise ValueError("Simulation period is not defined")

    logger = logging.getLogger(__name__)

    # Ensure that the output directory exists, or create it.
    io.ensure_directory_exists(ctx.settings['files']['output_directory'])

    # Initialise the summary object.
    ctx.component['summary'].initialise(ctx)

    logger.info("  {}  Estimating  from {} to {}".format(
        datetime.datetime.now().strftime("%H:%M:%S"), start, until))
    state = pfilter.run(ctx, start, until, ctx.data['obs'])
    forecasts = {'complete': state}

    # Save the observations (flattened into a single list).
    forecasts['obs'] = ctx.all_observations

    # Save the forecasting results to disk.
    if filename is not None:
        logger.info("  {}  Saving to:  {}".format(
            datetime.datetime.now().strftime("%H:%M:%S"), filename))
        # Save the results in the output directory.
        filepath = os.path.join(
            ctx.settings['files']['output_directory'], filename)
        ctx.component['summary'].save_forecasts(ctx, forecasts, filepath)

    return forecasts
