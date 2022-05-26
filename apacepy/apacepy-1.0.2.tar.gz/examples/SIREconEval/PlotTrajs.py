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
    S = A.TrajPlotInfo(outcome_name='In: Susceptible',
                       title='Susceptible',
                       x_multiplier=prev_multiplier)
    I = A.TrajPlotInfo(outcome_name='In: Infectious',
                       title='Infectious',
                       x_multiplier=prev_multiplier)
    R = A.TrajPlotInfo(outcome_name='In: Recovered',
                       title='Recovered',
                       x_multiplier=prev_multiplier)
    Inc = A.TrajPlotInfo(outcome_name='To: Infectious',
                         title='Incidence',
                         x_multiplier=incd_multiplier)

    sim_outcomes.plot_multi_panel(n_rows=2, n_cols=3,
                                  list_plot_info=[S, I, R, Inc],
                                  file_name='figures/SIRFigure.png')
