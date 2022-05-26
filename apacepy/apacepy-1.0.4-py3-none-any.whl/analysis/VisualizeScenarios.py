import apacepy.analysis.Scenarios as Cls
from apacepy.analysis.Scenarios import SetOfScenarios


def plot_sets_of_scenarios(list_of_scenario_sets,
                           name_of_base_scenario, effect_outcome, cost_outcome,
                           health_measure='d',
                           list_if_remove_base_scenario=None,
                           x_range=None, y_range=None,
                           effect_multiplier=1.0,
                           cost_multiplier=1.0,
                           switch_cost_effect_on_figure=False,
                           wtp_multiplier=1.0,
                           labels=('', ''),
                           title=None,
                           fig_size=None,
                           l_b_r_t=None,
                           file_name=None):
    """
    plots multiple sets of scenarios
    :param list_of_scenario_sets: (list) of scenario sets to display on the CE plane
            (each element is a SetOfScenarios)
    :param name_of_base_scenario: (string) name of the base strategy
    :param effect_outcome: (string) name of the effect outcome
    :param cost_outcome: (string) name of the cost outcome
    :param health_measure: ('d' or 'u') disutility or utility as the measure of effect
    :param list_if_remove_base_scenario: (list of Bool) if remove base scenarios from each scenario sets
        the default is (False, True, True, ...)
    :param x_range: x range
    :param y_range: y range
    :param effect_multiplier: the x-axis multiplier
    :param cost_multiplier: the y-axis multiplier
    :param switch_cost_effect_on_figure: displays cost on the x-axis and effect on the y-axis
    :param wtp_multiplier: wtp multiplier
    :param labels: (tuple) x_ and y-axis labels
    :param title: (string) title of the graph
    :param fig_size: (tuple) figure size
    :param file_name: (string) file name
    """

    for s in list_of_scenario_sets:
        assert isinstance(s, SetOfScenarios)

    # the default for removing the base strategy from a set of scenarios
    if list_if_remove_base_scenario is None:
        list_if_remove_base_scenario = [False]
        for s in range(len(list_of_scenario_sets) - 1):
            list_if_remove_base_scenario.append(True)

    # populate series
    Cls.SetOfScenarios.populate_sets_of_scenarios(
        list_of_scenario_sets=list_of_scenario_sets,
        effect_outcome=effect_outcome, cost_outcome=cost_outcome,
        name_of_base_scenario=name_of_base_scenario,
        list_if_remove_base_scenario=list_if_remove_base_scenario,
        health_measure=health_measure,
        save_cea_results=False,
        interval_type='c',
        effect_multiplier=effect_multiplier,
        cost_multiplier=cost_multiplier,
        switch_cost_effect_on_figure=switch_cost_effect_on_figure)

    # plot
    Cls.SetOfScenarios.plot_list_of_scenario_sets(
        list_of_scenario_sets=list_of_scenario_sets,
        x_label=labels[0],
        y_label=labels[1],
        title=title,
        show_only_on_frontier=False,
        x_range=x_range,
        y_range=y_range,
        show_error_bars=True,
        wtp_multiplier=wtp_multiplier,
        fig_size=fig_size,
        l_b_r_t=l_b_r_t,
        file_name=file_name)


def multi_plot_series(list_list_series,
                      list_of_titles,
                      name_of_base_scenario,
                      list_if_remove_base_scenario,
                      effect_outcome, cost_outcome,
                      x_range, y_range,
                      health_measure='u',
                      effect_multiplier=1.0,
                      cost_multiplier=1.0,
                      switch_cost_effect_on_figure=False,
                      wtp_multiplier=1.0,
                      labels=('', ''),
                      fig_size=None,
                      l_b_r_t=None,
                      file_name='fig.png'):
    """
    :param list_list_series: (list) of list of series to display on the multiple CE plane
    :param list_of_titles: (list) of titles
    :param name_of_base_scenario: (string) name of the base scenario
    :param list_if_remove_base_scenario:
    :param effect_outcome: (string) name of the effect outcome
    :param cost_outcome: (string) name of the cost outcome
    :param x_range: x range
    :param y_range: y range
    :param health_measure: ('d' or 'u') disutility or utility as the measure of effect
    :param effect_multiplier: the x-axis multiplier
    :param cost_multiplier: the y-axis multiplier
    :param switch_cost_effect_on_figure: displays cost on the x-axis and effect on the y-axis
    :param wtp_multiplier: wtp multiplier
    :param labels: (tuple) x_ and y-axis labels
    :param fig_size: (tuple) figure size
    :param l_b_r_t:
    :param file_name: (string) the file name to save the plot as
    """

    # populate series
    for list_series in list_list_series:
        Cls.SetOfScenarios.populate_sets_of_scenarios(
            list_of_scenario_sets=list_series,
            name_of_base_scenario=name_of_base_scenario,
            list_if_remove_base_scenario=list_if_remove_base_scenario,
            health_measure=health_measure,
            effect_outcome=effect_outcome,
            cost_outcome=cost_outcome,
            save_cea_results=False,
            interval_type='c',
            effect_multiplier=effect_multiplier,
            cost_multiplier=cost_multiplier,
            switch_cost_effect_on_figure=switch_cost_effect_on_figure)
    # plot
    Cls.SetOfScenarios.multi_plot_scenario_sets(
        list_of_plots=list_list_series,
        list_of_titles=list_of_titles,
        x_label=labels[0],
        y_label=labels[1],
        file_name=file_name,
        show_only_on_frontier=False,
        x_range=x_range,
        y_range=y_range,
        show_error_bars=True,
        wtp_multiplier=wtp_multiplier,
        fig_size=fig_size,
        l_b_r_t=l_b_r_t
    )
