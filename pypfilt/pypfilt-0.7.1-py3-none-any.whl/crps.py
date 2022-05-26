"""Calculate CRPS scores for simulated observations."""

import numpy as np


def crps_sample(true_values, samples_table):
    """
    Calculate the CRPS score for a table of samples drom from predictive
    distributions for multiple values, using the empirical distribution
    function defined by the provided samples.

    :param true_values: A 1-D array of observed values.
    :param samples_table: A 2-D array of samples, where each row contains the
        samples for the corresponding value in ``true_values``.
    """
    if np.ndim(true_values) != 1:
        raise ValueError('true_values must be a 1-D array')
    if np.ndim(samples_table) != 2:
        raise ValueError('samples_table must be a 2-D array')
    if len(true_values) != samples_table.shape[0]:
        raise ValueError('incompatible dimensions')
    return np.fromiter(
        (crps_edf_scalar(truth, samples_table[ix])
         for (ix, truth) in enumerate(true_values)),
        dtype=np.float_)


def crps_edf_scalar(true_value, samples):
    """
    Calculate the CRPS score for samples drawn from a predictive distribution
    for a single value, using the empirical distribution function defined by
    the provided samples.

    :param true_value: The (scalar) value that was observed.
    :param samples: Samples from the predictive distribution (a 1-D array).
    """
    c_1n = 1 / len(samples)
    x = np.sort(samples)
    a = np.arange(0.5 * c_1n, 1, c_1n)
    return 2 * c_1n * np.sum(((true_value < x) - a) * (x - true_value))


def simulated_obs_crps(true_obs, sim_obs):
    """
    Calculate CRPS scores for simulated observations, such as those recorded
    by the :class:`~pypfilt.summary.SimulatedObs` table, against observed
    values.

    The returned array has fields: ``'date'``, ``'fs_date'``, and ``'score'``.

    :param true_obs: The table of recorded observations; this must contain the
        fields ``'date'`` and ``'value``'.
    :param sim_obs: The table of simulated observations; this must contain the
        fields ``'fs_date'``, ``'date'``, and ``'value'``.

    :raises ValueError: if ``true_obs`` or ``sim_obs`` do not contain all of
        the required fields.
    """
    # Check that required columns are present.
    for column in ['date', 'value']:
        if column not in true_obs.dtype.names:
            msg_fmt = 'Column "{}" not found in true_obs'
            raise ValueError(msg_fmt.format(column))
    for column in ['fs_date', 'date', 'value']:
        if column not in sim_obs.dtype.names:
            msg_fmt = 'Column "{}" not found in sim_obs'
            raise ValueError(msg_fmt.format(column))

    # Only retain simulated observations for times with true observations.
    sim_mask = np.isin(sim_obs['date'], true_obs['date'])
    sim_obs = sim_obs[sim_mask]
    # Only retain true observations for times with simulated observations.
    true_mask = np.isin(true_obs['date'], sim_obs['date'])
    true_obs = true_obs[true_mask]

    # Identify the output rows.
    date_combs = np.unique(sim_obs[['fs_date', 'date']])
    score_rows = len(date_combs)
    time_dtype = true_obs.dtype.fields['date'][0]
    scores = np.zeros(
        (score_rows,),
        dtype=[('date', time_dtype),
               ('fs_date', time_dtype),
               ('score', np.float_)])

    # Calculate each CRPS score in turn.
    for (ix, (fs_date, date)) in enumerate(date_combs):
        # Ensure there is only a single true value for this date.
        true_mask = true_obs['date'] == date
        true_value = true_obs['value'][true_mask]
        true_count = len(true_value)
        if true_count != 1:
            msg_fmt = 'Found {} true values for {}'
            raise ValueError(msg_fmt.format(true_count, date))
        true_value = true_value[0]

        # Calculate the CRPS for this date.
        sim_mask = np.logical_and(
            sim_obs['date'] == date, sim_obs['fs_date'] == fs_date)
        samples = sim_obs['value'][sim_mask]
        score = crps_edf_scalar(true_value, samples)

        # Update the current row of the scores table.
        scores['date'][ix] = date
        scores['fs_date'][ix] = fs_date
        scores['score'][ix] = score

    return scores
