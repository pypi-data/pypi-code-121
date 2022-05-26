#!/usr/bin/env python
"""
An example of using the ``pypfilt`` package to estimate the state of a
two-species system described by the Lotka-Volterra equations.
"""

import pypfilt
import pypfilt.summary
import numpy as np
import numpy.lib.recfunctions as rf
import scipy.integrate
import scipy.stats
import h5py
import pypfilt.plot
import logging
import sys
import pkgutil


class LotkaVolterra(pypfilt.Model):
    """An implementation of the (continuous) Lotka-Volterra equations."""

    __field_names = ['x', 'y', 'alpha', 'beta', 'gamma', 'delta']

    def __init__(self):
        # Record the state vector data type.
        self.dtype = np.dtype(self.field_types(ctx=None))

    def init(self, ctx, vec):
        """Initialise a matrix of state vectors."""
        prior = ctx.data['prior']
        for name in self.__field_names:
            vec[name] = prior[name]

    def field_types(self, ctx):
        return [(name, np.float_) for name in self.__field_names]

    def d_dt(self, xt, t):
        """Calculate the derivatives of x(t) and y(t)."""
        # Restore the 2D shape of the flattened state matrix.
        xt = xt.reshape((-1, 6))
        d_dt = np.zeros(xt.shape)
        xt = xt.view(self.dtype).reshape(-1)
        x, y = xt['x'], xt['y']
        # Calculate dx/dt and dy/dt.
        d_dt[..., 0] = xt['alpha'] * x - xt['beta'] * x * y
        d_dt[..., 1] = xt['gamma'] * x * y - xt['delta'] * y
        # Flatten the 2D derivatives matrix.
        return d_dt.reshape(-1)

    def update(self, ctx, t, dt, is_fs, prev, curr):
        """Perform a single time-step."""
        # Use scalar time, so that ``t + dt`` is well-defined.
        t = ctx.component['time'].to_scalar(t)
        # The state matrix must be converted to a float array for odeint.
        prev_r = prev.view((float, 6)).reshape(-1)
        xt = scipy.integrate.odeint(self.d_dt, prev_r,
                                    [t, t + dt])[1]
        # Restore the 2D shape of the flattened state matrix.
        curr[:] = xt.view(self.dtype)

    def can_smooth(self):
        return {'alpha', 'beta', 'gamma', 'delta'}


class ObsModel(pypfilt.obs.Univariate):
    def __init__(self, obs_unit, settings):
        super().__init__(obs_unit)
        self.sdev = settings['parameters']['sdev']

    def distribution(self, ctx, snapshot, ixs=None):
        if self.unit == 'x':
            expected = snapshot.vec['state_vec']['x']
        elif self.unit == 'y':
            expected = snapshot.vec['state_vec']['y']
        else:
            raise ValueError('invalid observation unit: {}'.format(self.unit))
        if ixs is not None:
            expected = expected[ixs]
        return scipy.stats.norm(loc=expected, scale=self.sdev)


def default_priors():
    """Define default model prior distributions."""
    return {
        'x': lambda r, size=None: r.uniform(0.5, 1.5, size=size),
        'y': lambda r, size=None: r.uniform(0.2, 0.4, size=size),
        'alpha': lambda r, size=None: r.uniform(0.6, 0.8, size=size),
        'beta': lambda r, size=None: r.uniform(1.2, 1.4, size=size),
        'gamma': lambda r, size=None: r.uniform(0.9, 1.1, size=size),
        'delta': lambda r, size=None: r.uniform(0.9, 1.1, size=size),
    }


def predation_instance(toml_file):
    """
    Return an instance of the predation scenario from the specified TOML file.
    """
    write_example_files()
    instances = list(pypfilt.scenario.load_instances(toml_file))
    assert len(instances) == 1
    instance = instances[0]
    return instance


def predation_scalar_instance():
    """
    Return an instance of the predation scenario using a scalar time scale.
    """
    return predation_instance('predation.toml')


def predation_datetime_instance():
    """
    Return an instance of the predation scenario using a datetime time scale.
    """
    return predation_instance('predation-datetime.toml')


def apply_ground_truth_prior(instance):
    """
    Define the predation model prior distribution for fixed ground truth.
    """
    x0 = 0.9
    y0 = 0.25
    alpha = 2/3
    beta = 4/3
    gamma = 1
    delta = 1
    instance.settings['prior'] = {
        'x': {
            'name': 'uniform',
            'args': {'low': x0, 'high': x0}},
        'y': {
            'name': 'uniform',
            'args': {'low': y0, 'high': y0}},
        'alpha': {
            'name': 'uniform',
            'args': {'low': alpha, 'high': alpha}},
        'beta': {
            'name': 'uniform',
            'args': {'low': beta, 'high': beta}},
        'gamma': {
            'name': 'uniform',
            'args': {'low': gamma, 'high': gamma}},
        'delta': {
            'name': 'uniform',
            'args': {'low': delta, 'high': delta}},
    }


def save_scalar_observations(obs_tables, x_obs_file, y_obs_file):
    """Save simulated observations to disk."""
    want_columns = ['date', 'value']
    x_tbl = obs_tables['x'][want_columns]
    y_tbl = obs_tables['y'][want_columns]
    x_tbl = x_tbl[x_tbl['date'] > 0]
    y_tbl = y_tbl[y_tbl['date'] > 0]
    np.savetxt(x_obs_file, x_tbl, fmt='%d %f',
               header='date value', comments='')
    np.savetxt(y_obs_file, y_tbl, fmt='%d %f',
               header='date value', comments='')


def save_datetime_observations(obs_tables, x_obs_file, y_obs_file):
    """Save simulated observations to disk."""
    # Make the 'date' column contain strings, not byte strings.
    # Note that this also removes the time-stamp.
    want_columns = ['date', 'value']
    x_tbl = obs_tables['x'][want_columns]
    y_tbl = obs_tables['y'][want_columns]
    x_date_strs = [d.strftime('%Y-%m-%d') for d in x_tbl['date']]
    y_date_strs = [d.strftime('%Y-%m-%d') for d in y_tbl['date']]
    # NOTE: must use ['value'] instead of 'value' here.
    x_tbl = rf.append_fields(x_tbl[['value']], 'date', x_date_strs)
    y_tbl = rf.append_fields(y_tbl[['value']], 'date', y_date_strs)
    x_tbl = x_tbl[x_tbl['date'] != x_tbl['date'][0]]
    y_tbl = y_tbl[y_tbl['date'] != y_tbl['date'][0]]
    # NOTE: reorder the fields so that 'date' comes first.
    x_tbl = x_tbl[want_columns]
    y_tbl = y_tbl[want_columns]
    np.savetxt(x_obs_file, x_tbl, fmt='%s %f',
               header='date value', comments='')
    np.savetxt(y_obs_file, y_tbl, fmt='%s %f',
               header='date value', comments='')


def forecast(data_file):
    """
    Run a suite of forecasts against generated observations, using a scalar
    time scale.

    :param date_file: The name of the output HDF5 file.
    """
    logger = logging.getLogger(__name__)
    logger.info('Preparing the forecast simulations')

    # Define the simulation period and forecasting times.
    instance = predation_scalar_instance()
    fs_times = [1.0, 3.0, 5.0, 7.0, 9.0]

    # Simulate observations from a known ground truth.
    apply_ground_truth_prior(instance)
    obs_tables = pypfilt.simulate_from_model(instance)

    # Run forecasts against these simulated observations.
    instance = predation_instance('predation.toml')
    for obs_unit in obs_tables.keys():
        instance.settings['summary']['tables'][obs_unit] = {
            'component': 'pypfilt.summary.SimulatedObs',
            'observation_unit': obs_unit,
        }
    instance.settings['summary']['tables']['param_cover'] = {
        'component': 'pypfilt.summary.ParamCovar',
    }

    context = instance.build_context(obs_tables=obs_tables)

    state = pypfilt.forecast(context, fs_times, filename=data_file)
    return state


def plot_forecasts(state_cints, x_obs, y_obs, pdf_file=None, png_file=None):
    """Plot the population predictions at each forecasting date."""
    logger = logging.getLogger(__name__)
    with pypfilt.plot.apply_style():
        plot = pypfilt.plot.Grid(
            state_cints, 'Time', 'Population Size (1,000s)',
            ('fs_date', 'Forecast @ t = {:0.0f}'),
            ('unit', lambda s: '{}(t)'.format(s)))
        plot.expand_x_lims('date')
        plot.expand_y_lims('ymax')

        for (ax, df) in plot.subplots():
            ax.axhline(y=0, xmin=0, xmax=1,
                       linewidth=1, linestyle='--', color='k')
            hs = pypfilt.plot.cred_ints(ax, df, 'date', 'prob')
            if df['unit'][0] == 'x':
                df_obs = x_obs
            else:
                df_obs = y_obs
            past_obs = df_obs[df_obs['date'] <= df['fs_date'][0]]
            future_obs = df_obs[df_obs['date'] > df['fs_date'][0]]
            hs.extend(pypfilt.plot.observations(ax, past_obs,
                                                label='Past observations'))
            hs.extend(pypfilt.plot.observations(ax, future_obs,
                                                future=True,
                                                label='Future observations'))
            plot.add_to_legend(hs)

            # Adjust the axis limits and the number of ticks.
            ax.set_xlim(left=0)
            ax.locator_params(axis='x', nbins=4)
            ax.set_ylim(bottom=-0.2)
            ax.locator_params(axis='y', nbins=4)

        plot.legend(loc='upper center', ncol=5)

        if pdf_file:
            logger.info('Plotting to {}'.format(pdf_file))
            plot.save(pdf_file, format='pdf', width=10, height=5)
        if png_file:
            logger.info('Plotting to {}'.format(png_file))
            plot.save(png_file, format='png', width=10, height=5)


def plot_params(param_cints, pdf_file=None, png_file=None):
    """Plot the parameter posteriors over the estimation run."""
    logger = logging.getLogger(__name__)
    with pypfilt.plot.apply_style():
        plot = pypfilt.plot.Wrap(
            param_cints, 'Time', 'Value',
            ('name', lambda s: '$\\{}$'.format(s)),
            nr=1)
        plot.expand_y_lims('ymax')

        for (ax, df) in plot.subplots(dy=-0.025):
            hs = pypfilt.plot.cred_ints(ax, df, 'date', 'prob')
            if df['name'][0] == 'alpha':
                y_true = 2/3
            elif df['name'][0] == 'beta':
                y_true = 4/3
            elif df['name'][0] == 'gamma':
                y_true = 1
            elif df['name'][0] == 'delta':
                y_true = 1
            hs.append(ax.axhline(y=y_true, xmin=0, xmax=1, label='True value',
                                 linewidth=1, linestyle='--', color='k'))
            plot.add_to_legend(hs)

        plot.legend(loc='upper center', ncol=5, borderaxespad=0)

        if pdf_file:
            logger.info('Plotting to {}'.format(pdf_file))
            plot.save(pdf_file, format='pdf', width=10, height=3)
        if png_file:
            logger.info('Plotting to {}'.format(png_file))
            plot.save(png_file, format='png', width=10, height=3)


def plot(data_file, png=True, pdf=True):
    """
    Save the plots produced by :func:`plot_params` and :func:`plot_forecasts`.

    This will save the plots to files whose names begin with
    "predation_params" and "predation_forecasts".

    :param png: Whether to save plots as PNG files.
    :param pdf: Whether to save plots as PDF files.
    """
    logger = logging.getLogger(__name__)
    logger.info('Loading outputs from {}'.format(data_file))

    # Use the 'Agg' backend so that plots can be generated non-interactively.
    import matplotlib
    matplotlib.use('Agg')

    # File names for the generated plots.
    fs_pdf = 'predation_forecasts.pdf'
    fs_png = 'predation_forecasts.png'
    pp_pdf = 'predation_params.pdf'
    pp_png = 'predation_params.png'

    time_scale = pypfilt.Scalar()

    # Read in the model credible intervals and the observations.
    with h5py.File(data_file, 'r') as f:
        cints = pypfilt.io.load_dataset(time_scale, f['/tables/model_cints'])
        forecasts = pypfilt.io.load_dataset(time_scale, f['/tables/forecasts'])
        x_obs = pypfilt.io.load_dataset(time_scale, f['/observations/x'])
        y_obs = pypfilt.io.load_dataset(time_scale, f['/observations/y'])

    # Separate the credible intervals for the population sizes from the
    # credible intervals for the model parameters.
    var_mask = np.logical_or(cints['name'] == 'x',
                             cints['name'] == 'y')
    param_cints = cints[np.logical_not(var_mask)]

    # Only retain forecasts, ignore results from the estimation pass, if any.
    fs_mask = forecasts['fs_date'] < max(forecasts['date'])
    forecasts = forecasts[fs_mask]

    # Only keep the model parameter posteriors from the estimation run.
    est_mask = param_cints['fs_date'] == max(param_cints['date'])
    param_cints = param_cints[est_mask]

    # Plot the population forecasts.
    pdf_file = fs_pdf if pdf else None
    png_file = fs_png if png else None
    plot_forecasts(forecasts, x_obs, y_obs, pdf_file, png_file)

    # Plot the model parameter posterior distributions.
    pdf_file = pp_pdf if pdf else None
    png_file = pp_png if png else None
    plot_params(param_cints, pdf_file, png_file)


def __example_data(filename):
    return pkgutil.get_data('pypfilt.examples', filename).decode()


def example_toml_data():
    """Return the contents of the example file "predation.toml"."""
    return __example_data('predation.toml')


def example_obs_x_data():
    """Return the contents of the example file "predation-counts-x.ssv"."""
    return __example_data('predation-counts-x.ssv')


def example_obs_y_data():
    """Return the contents of the example file "predation-counts-y.ssv"."""
    return __example_data('predation-counts-y.ssv')


def example_toml_datetime_data():
    """Return the contents of the example file "predation-datetime.toml"."""
    return __example_data('predation-datetime.toml')


def example_obs_x_datetime_data():
    """
    Return the contents of the example file "predation-counts-x-datetime.ssv".
    """
    return __example_data('predation-counts-x-datetime.ssv')


def example_obs_y_datetime_data():
    """
    Return the contents of the example file "predation-counts-y-datetime.ssv".
    """
    return __example_data('predation-counts-y-datetime.ssv')


def write_example_files():
    """
    Save the following example files to the working directory:

    * The forecast scenario file "predation.toml";
    * The observations file "predation-counts-x.ssv";
    * The observations file "predation-counts-y.ssv";
    * The forecast scenario file "predation-datetime.toml";
    * The observations file "predation-counts-x-datetime.ssv"; and
    * The observations file "predation-counts-y-datetime.ssv";
    """

    file_names = [
        'predation.toml',
        'predation-counts-x.ssv',
        'predation-counts-y.ssv',
        'predation-datetime.toml',
        'predation-counts-x-datetime.ssv',
        'predation-counts-y-datetime.ssv',
    ]

    for file_name in file_names:
        content = __example_data(file_name)
        with open(file_name, 'w') as f:
            f.write(content)


def main(args=None):
    logging.basicConfig(level=logging.INFO)
    data_file = 'predation.hdf5'
    forecast(data_file)
    plot(data_file, pdf=False)


if __name__ == '__main__':
    sys.exit(main())
