import apacepy.analysis.Trajectories as A


def plot(prev_multiplier=52, incd_multiplier=1):
    """
    :param prev_multiplier: (int) to multiply the simulation time to convert it to year, week, or day.
    :param incd_multiplier: (int) to multiply the simulation period to covert it to year, week, or day.
    :return:
    """

    sim_outcomes = A.SimOutcomeTrajectories(csv_directory='outputs/trajectories/')

    # defaults
    A.X_TICKS = [0, 5]  # x-axis ticks (min at 0 with interval of 5)
    A.X_LABEL = 'Weeks'  # x-axis label

    # plot information
    SCh = A.TrajPlotInfo(outcome_name='In: Susceptible Children',
                         title='Susceptible Children',
                         x_multiplier=prev_multiplier)
    ICh = A.TrajPlotInfo(outcome_name='In: Infectious Children',
                         title='Infectious Children',
                         x_multiplier=prev_multiplier)
    RCh = A.TrajPlotInfo(outcome_name='In: Recovered Children',
                         title='Recovered Children',
                         x_multiplier=prev_multiplier)
    SAd = A.TrajPlotInfo(outcome_name='In: Susceptible Adults',
                         title='Susceptible Adults',
                         x_multiplier=prev_multiplier)
    IAd = A.TrajPlotInfo(outcome_name='In: Infectious Adults',
                         title='Infectious Adults',
                         x_multiplier=prev_multiplier)
    RAd = A.TrajPlotInfo(outcome_name='In: Recovered Adults',
                         title='Recovered Adults',
                         x_multiplier=prev_multiplier)

    Prev = A.TrajPlotInfo(outcome_name='Prevalence',
                          title='Prevalence',
                          x_multiplier=prev_multiplier)
    PrevCh = A.TrajPlotInfo(outcome_name='% prevalence | children',
                            title='Prevalence |\nChildren (%)',
                            x_multiplier=prev_multiplier, y_multiplier=100, y_range=(0, 100))
    PrevAd = A.TrajPlotInfo(outcome_name='% prevalence | adults',
                            title='Prevalence |\nAdults (%)',
                            x_multiplier=prev_multiplier, y_multiplier=100, y_range=(0, 100))

    Inc = A.TrajPlotInfo(outcome_name='Incidence',
                         title='Incidence',
                         x_multiplier=incd_multiplier)
    IncCh = A.TrajPlotInfo(outcome_name='% incidence | children',
                           title='Incidence |\nChildren (%)',
                           x_multiplier=incd_multiplier, y_multiplier=100, y_range=(0, 100))
    IncAd = A.TrajPlotInfo(outcome_name='% incidence | adults',
                           title='Incidence |\nAdults (%)',
                           x_multiplier=incd_multiplier, y_multiplier=100, y_range=(0, 100))

    CumInc = A.TrajPlotInfo(outcome_name='Cumulative incidence',
                            title='Cumulative Incidence',
                            x_multiplier=prev_multiplier)
    CumIncCh = A.TrajPlotInfo(outcome_name='% total incidence | children',
                              title='Cumulative Incidence |\nChildren (%)',
                              x_multiplier=prev_multiplier, y_multiplier=100, y_range=(0, 100))
    CumIncAd = A.TrajPlotInfo(outcome_name='% total incidence | adults',
                              title='Cumulative Incidence |\nAdults (%)',
                              x_multiplier=prev_multiplier, y_multiplier=100, y_range=(0, 100))

    sim_outcomes.plot_multi_panel(n_rows=5, n_cols=3,
                                  list_plot_info=[SCh, ICh, RCh,
                                                  SAd, IAd, RAd,
                                                  Prev, PrevCh, PrevAd,
                                                  Inc, IncCh, IncAd,
                                                  CumInc, CumIncAd, CumIncCh],
                                  figure_size=(5, 7),
                                  file_name='figures/SIRAgeStructuredFigure.png')
