import apacepy.analysis.Scenarios as S
import apacepy.analysis.Trajectories as A


def plot_trajs(schools_closed=False, decision_rule='time-based',
               prev_multiplier=52, incd_multiplier=1, obs_incd_multiplier=1):
    """
    :param schools_closed: (bool)
    :param decision_rule: (string) 'time-based' or 'threshold-based'
    :param prev_multiplier: (int) to multiply the simulation time to convert it to year, week, or day.
    :param incd_multiplier: (int) to multiply the simulation period to covert it to year, week, or day.
    :param obs_incd_multiplier: (int) to multiply the observation period to convert it year, week, or day
    :return:
    """

    if schools_closed:
        directory = 'outputs/trajectories/closed-'+decision_rule+'/'
    else:
        directory = 'outputs/trajectories/open'

    sim_outcomes = A.SimOutcomeTrajectories(csv_directory=directory)

    # defaults
    A.X_TICKS = [0, 5]  # x-axis ticks (min at 0 with interval of 5)
    A.X_RANGE = [0, 20]
    A.X_LABEL = 'Weeks'  # x-axis label

    # plot information
    SCh = A.TrajPlotInfo(outcome_name='In: Susceptible Children',
                         title='Susceptible Children',
                         x_multiplier=prev_multiplier)
    ICh = A.TrajPlotInfo(outcome_name='In: Infectious Children',
                         title='Infectious Children',
                         x_multiplier=prev_multiplier,
                         y_range=(0, 200))
    RCh = A.TrajPlotInfo(outcome_name='In: Recovered Children',
                         title='Recovered Children',
                         x_multiplier=prev_multiplier,
                         y_range=(0, 1000))
    SAd = A.TrajPlotInfo(outcome_name='In: Susceptible Adults',
                         title='Susceptible Adults',
                         x_multiplier=prev_multiplier)
    IAd = A.TrajPlotInfo(outcome_name='In: Infectious Adults',
                         title='Infectious Adults',
                         x_multiplier=prev_multiplier,
                         y_range=(0, 400))
    RAd = A.TrajPlotInfo(outcome_name='In: Recovered Adults',
                         title='Recovered Adults',
                         x_multiplier=prev_multiplier,
                         y_range=(0, 2000))

    Prev = A.TrajPlotInfo(outcome_name='Prevalence',
                          title='Prevalence',
                          x_multiplier=prev_multiplier,
                          y_range=(0, 500))
    Inc = A.TrajPlotInfo(outcome_name='Obs: Incidence',
                         title='Observed Incidence',
                         x_multiplier=obs_incd_multiplier,
                         y_range=(0, 750))
    CumInc = A.TrajPlotInfo(outcome_name='Cumulative incidence',
                            title='Cumulative Incidence',
                            x_multiplier=prev_multiplier,
                            y_range=(0, 3000))

    if schools_closed:
        filename = 'figures/schools-closed-{}.png'.format(decision_rule)
    else:
        filename = 'figures/schools-open.png'

    sim_outcomes.plot_multi_panel(n_rows=3, n_cols=3,
                                  list_plot_info=[SCh, ICh, RCh, SAd, IAd, RAd, Prev, Inc, CumInc],
                                  file_name=filename)


def plot_cea(scenario_names):

    # read scenarios into a dataframe
    scenarios_df = S.ScenarioDataFrame(csv_file_name='scenarios/scenario_analysis.csv')

    # get an specific outcome from an specific scenario
    for name in scenario_names:
        print('\nIncidence of {}:'.format(name)
              + scenarios_df.get_mean_interval(scenario_name=name, outcome_name='Incidence'))

