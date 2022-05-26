import apacepy.analysis.Scenarios as S
import apacepy.analysis.VisualizeScenarios as V

S.ERROR_BAR_ALPHA = 0.2
SHOW_DYNAMIC = True


def plot_scenarios(fig_file_name):

    # read scenarios into a dataframe
    df_threshold_based = S.ScenarioDataFrame(
        csv_file_name='scenarios/scenarios-threshold-based.csv')
    if SHOW_DYNAMIC:
        df_dynamic = S.ScenarioDataFrame(
            csv_file_name='scenarios/scenarios-dynamic.csv')

    # sets of scenarios to display on the cost-effectiveness plain
    threshold_based_scenarios = S.SetOfScenarios(
        name='Threshold-Based',
        scenario_df=df_threshold_based,
        color='blue',
        marker='o',
        conditions_on_variables=[
            S.ConditionOnVariable(var_name='decision rule', values='threshold-based'),
            S.ConditionOnVariable(var_name='threshold-on', if_included_in_label=True,
                                  label_format='{:.0f}'),
            S.ConditionOnVariable(var_name='threshold-off', if_included_in_label=True,
                                  label_format='{:.0f}')],
        if_find_frontier=False,
        if_show_fitted_curve=True,
        labels_shift_x=0.03,
        labels_shift_y=0.00)

    if SHOW_DYNAMIC:
        dynamic_scenarios = S.SetOfScenarios(
            name='Dynamic',
            scenario_df=df_dynamic,
            color='red',
            marker='o',
            conditions_on_variables=[
                S.ConditionOnVariable(var_name='decision rule', values='dynamic'),
                S.ConditionOnVariable(var_name='wtp', if_included_in_label=True,
                                      label_format='{:.2f}')],
            if_find_frontier=False,
            if_show_fitted_curve=True,
            labels_shift_x=-0.07,
            labels_shift_y=0.01)

    # plot
    if SHOW_DYNAMIC:
        list_of_scenario_sets = [threshold_based_scenarios, dynamic_scenarios]
    else:
        list_of_scenario_sets = [threshold_based_scenarios]
    V.plot_sets_of_scenarios(list_of_scenario_sets=list_of_scenario_sets,
                             name_of_base_scenario='No closure',
                             effect_outcome='Incidence (after epidemic warm-up)',
                             cost_outcome='Duration of School closure',
                             labels=('Cases Averted', 'Weeks with Schools Closed'),
                             x_range=(0, 400), y_range=(0, 0.25*52), cost_multiplier=52,
                             file_name=fig_file_name,
                             fig_size=(4, 4))


if __name__ == "__main__":

    plot_scenarios(fig_file_name='figures/scenario_analysis')
