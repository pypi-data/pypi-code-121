import warnings

from deampy.in_out_functions import write_columns_to_csv

from apacepy.time_series import SumPrevalence, SumIncidence, SumCumulativeIncidence

warnings.simplefilter('always')


def export_trajectories(id, seed, epi_history, decision_maker, folder_trajectories, delete_existing_files=True):
    """
    :param id: id of this simulated trajectory
    :param seed: seed that generated this trajectory
    :param epi_history: the epidemic history
    :param decision_maker: the decision maker
    :param folder_trajectories: folder where this trajectory should be saved.
    :param delete_existing_files: set to True to delete the existing trace files in the specified directory
    """

    file_name = 'trajectory {} - {}.csv'.format(id, seed)

    cols = []

    # time-based simulation outputs
    sim_times = [row[0] for row in epi_history.timeMonitor.simTimesAndSimPeriods]
    _add_column(cols=cols, col_title='Simulation Time', values=sim_times)
    _add_prev(cols=cols, nodes=epi_history.compartments)
    _add_prev(cols=cols, nodes=epi_history.queueCompartments)
    _add_accum_incd(cols=cols, nodes=epi_history.compartments)
    _add_accum_incd(cols=cols, nodes=epi_history.chanceNodes)

    # sanity check
    # for s in epi_history.sumTimeSeries:
    #     if not any(s.get_sim_time_series()):
    #         message = "All values of sum time-series '{}' is None. " \
    #                   "Make sure that this time-series " \
    #                   "is passed in the function that populates the model.".format(s.name)
    #         warnings.warn(message)
    # for r in epi_history.ratioTimeSeries:
    #     if not any(r.simTimeSeries):
    #         message = "All values of ratio time-series '{}' is None. " \
    #                   "Make sure that sum time-series defining this ratio time-series " \
    #                   "are passed in the function that populates the model.".format(r.name)
    #         warnings.warn(message)

    for s in epi_history.sumTimeSeries:
        if isinstance(s, SumPrevalence) or isinstance(s, SumCumulativeIncidence):
            _add_column(cols=cols, col_title=s.name, values=s.timeSeries)
    for r in epi_history.ratioTimeSeries:
        if r.type in ('prev/prev', 'cum-incd/cum-incd', 'cum-incd/prev'):
            _add_column(cols=cols, col_title=r.name, values=r.simTimeSeries)

    # period-based simulation outputs
    output_periods = [row[1] for row in epi_history.timeMonitor.simTimesAndSimPeriods]
    _add_column(cols=cols, col_title='Simulation Period', values=output_periods)
    _add_incd(cols=cols, nodes=epi_history.compartments)
    _add_incd(cols=cols, nodes=epi_history.chanceNodes)
    _add_incd(cols=cols, nodes=epi_history.queueCompartments)

    for s in epi_history.sumTimeSeries:
        if isinstance(s, SumIncidence):
            _add_column(cols=cols, col_title=s.name, values=s.get_sim_time_series())
    for r in epi_history.ratioTimeSeries:
        if r.type in ('incd/incd', 'incd/prev', 'incd/cum-incd'):
            _add_column(cols=cols, col_title=r.name, values=r.simTimeSeries)
    _add_column(cols=cols, col_title='Interventions', values=decision_maker.statusOfIntvsOverPastSimOutPeriods)

    # surveyed outputs
    if epi_history.ifAnySurveillance:
        # time-based observation outputs
        obs_times = [row[0] for row in epi_history.timeMonitor.surveyTimesAndSurveyPeriods]
        _add_column(cols=cols, col_title='Observation Time', values=obs_times)

        for s in epi_history.sumTimeSeries:
            if s.surveillance:
                if isinstance(s, SumPrevalence) or isinstance(s, SumCumulativeIncidence):
                    _add_column(cols=cols, col_title='Obs: ' + s.name,
                                values=s.surveillance.surveyedTimeSeries)
        for r in epi_history.ratioTimeSeries:
            if r.ifSurveyed:
                if r.type in ('prev/prev', 'cum-incd/cum-incd', 'cum-incd/prev'):
                    _add_column(cols=cols, col_title='Obs: ' + r.name, values=r.surveyedTimeSeries)

        # period-based observation outputs
        obs_periods = [row[1] for row in epi_history.timeMonitor.surveyTimesAndSurveyPeriods]
        _add_column(cols=cols, col_title='Observation Period', values=obs_periods)

        for s in epi_history.sumTimeSeries:
            if s.surveillance:
                if isinstance(s, SumIncidence):
                    _add_column(cols=cols, col_title='Obs: ' + s.name,
                                values=s.surveillance.surveyedTimeSeries)
        for r in epi_history.ratioTimeSeries:
            if r.ifSurveyed:
                if r.type in ('incd/incd', 'incd/prev', 'incd/cum-incd'):
                    _add_column(cols=cols, col_title='Obs: ' + r.name, values=r.surveyedTimeSeries)

        _add_column(cols=cols, col_title='Obs: Interventions',
                    values=decision_maker.statusOfIntvsOverPastObsPeriods)

    # export
    write_columns_to_csv(cols=cols, file_name=file_name,
                         directory=folder_trajectories,
                         delete_existing_files=delete_existing_files)


def _add_prev(cols, nodes):
    for c in nodes:
        if c.history is not None:
            if c.history.prevSeries is not None:
                _add_column(cols=cols, col_title='In: ' + c.name,
                            values=c.history.prevSeries)


def _add_accum_incd(cols, nodes):
    for c in nodes:
        if c.history is not None:
            if c.history.cumIncdSeries is not None:
                _add_column(cols=cols, col_title='Total to: ' + c.name,
                            values=c.history.cumIncdSeries)


def _add_incd(cols, nodes):
    for c in nodes:
        if c.history is not None:
            if c.history.incdSeries is not None:
                _add_column(cols=cols, col_title='To: ' + c.name,
                            values=c.history.incdSeries.timeSeries)


def _add_column(cols, col_title, values):
    col = [col_title]
    col.extend(values)
    cols.append(col)


def append_to_a_dict(existing_dict, new_dict):
    """ appends a new dictionary to an existing dictionary with the same keys
    :param existing_dict: (dict)
    :param new_dict: (dict)
    """

    for key, value in new_dict.items():
        if key in existing_dict:
            existing_dict[key].append(value)
        else:
            existing_dict[key] = [value]


def extend_a_dict(existing_dict, new_dict):
    """ extend an existing dictionary with a new dictionary with the same keys
    :param existing_dict: (dict)
    :param new_dict: (dict)
    """

    for key, value in new_dict.items():
        if key in existing_dict:
            existing_dict[key].extend(value)
        else:
            existing_dict[key] = value


