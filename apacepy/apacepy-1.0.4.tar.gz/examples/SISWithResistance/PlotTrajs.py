import apacepy.analysis.Trajectories as A


def plot(prev_multiplier=52, incd_multiplier=1):
    """
    :param prev_multiplier: (int) to multiply the simulation time to convert it to year, week, or day.
    :param incd_multiplier: (int) to multiply the simulation period to covert it to year, week, or day.
    :return:
    """

    sim_outcomes = A.SimOutcomeTrajectories(csv_directory='outputs/trajectories')

    # defaults
    A.X_TICKS = [0, 5]  # x-axis ticks (min at 0 with interval of 5)
    A.X_LABEL = 'Weeks'  # x-axis label

    # plot information
    S = A.TrajPlotInfo(outcome_name='In: Sus',
                       title='Susceptible',
                       x_multiplier=prev_multiplier)
    I_S = A.TrajPlotInfo(outcome_name='In: Inf-Sus',
                         title='Infectious-Drug Susceptible)',
                         x_multiplier=prev_multiplier)
    I_R = A.TrajPlotInfo(outcome_name='In: Inf-Res',
                         title='Infectious-Drug Resistant',
                         x_multiplier=prev_multiplier)
    To_I_S = A.TrajPlotInfo(outcome_name='To: Inf-Sus',
                            title='New DS-Infection',
                            x_multiplier=incd_multiplier)
    To_I_R = A.TrajPlotInfo(outcome_name='To: Inf-Res',
                            title='New DR-Infection',
                            x_multiplier=incd_multiplier)

    sim_outcomes.plot_multi_panel(n_rows=2, n_cols=3,
                                  list_plot_info=[S, I_S, I_R, To_I_S, To_I_R],
                                  file_name='figures/fig.png')
