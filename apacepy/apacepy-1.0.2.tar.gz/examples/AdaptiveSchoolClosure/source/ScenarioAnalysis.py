
INCIDENCE_MIN_MAX_STEP = (50, 450, 50)
# variable names (these correspond to the argument of the method update_settings of ModelSettings)
VAR_NAMES = ['If schools closed', 'decision rule',
             'time-on', 'time-off', 'threshold-on', 'threshold-off',
             'dynamic type', 'wtp']
BASE_SCENARIO = [True, 'time-based',
                 100*52, 100*52, None, None,
                 None, None]


def get_threshold_based_scenario_names_vars_definitions():

    # create thresholds (on, off)
    thresholds = []
    for off_threshold in range(INCIDENCE_MIN_MAX_STEP[0], INCIDENCE_MIN_MAX_STEP[1], INCIDENCE_MIN_MAX_STEP[2]):
        on_threshold = off_threshold
        thresholds.append([on_threshold, off_threshold])

    # names of the scenarios to evaluate
    scenario_names = ['No closure']
    for t in thresholds:
        scenario_names.append('Incidence thresholds '+str(t))

    # variable values
    # for the scenario when schools are never closed
    scenario_definitions = [BASE_SCENARIO]

    # for the scenarios with threshold-based decision rules
    for t in thresholds:
        scenario_definitions.append([True, 'threshold-based', None, None, t[0], t[1], None, None])

    return scenario_names, VAR_NAMES, scenario_definitions


def get_dynamic_scenario_names_vars_definitions(wtp_values, dynamic_type):
    """
    :param wtp_values: (list) of willingness-to-pay values
    :param dynamic_type: 'cum incd' for using cumulative incidence as feature
             'incd + cum incd' for using incidence and cumulative incidence as feature
             'incd + pd status' for using incidence and the status of physical distancing intervention
             as feature
    """

    # names of the scenarios to evaluate
    scenario_names = ['No closure']
    for wtp in wtp_values:
        scenario_names.append('Dynamic WTP '+str(wtp))

    # for the scenario when schools are never closed
    scenario_definitions = [BASE_SCENARIO]

    # variable values
    # for the scenarios with dynamic decision rules
    for wtp in wtp_values:
        scenario_definitions.append([True, 'dynamic', None, None, None, None, dynamic_type, wtp])

    return scenario_names, VAR_NAMES, scenario_definitions
