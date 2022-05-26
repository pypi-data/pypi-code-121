import apacepy.Calibration as calib
from apacepy.ScenarioSimulation import ScenarioSimulator

import examples.SchoolClosure.SchoolClosureModel as M
from source.ScenarioAnalysis import get_threshold_based_scenario_names_vars_definitions, \
    get_dynamic_scenario_names_vars_definitions

N = 50
WTP_VALUES = [0.02]


def simulate_scenarios(decision_rule='threshold_based', dynamic_type=None, wtp_values=None):
    """
    :param decision_rule: (string) 'time-based', 'threshold-based', or 'dynamic'
    :param dynamic_type: 'cum incd' for using cumulative incidence as feature
         'incd + cum incd' for using incidence and cumulative incidence as feature
         'incd + pd status' for using incidence and the status of physical distancing intervention
         as feature
    :param wtp_values: (list) of willingness-to-pay values
    """

    # get model settings
    sets = M.SchoolClosureSettings()
    sets.exportTrajectories = False

    # get scenario names, variable names, and scenario definitions
    if decision_rule == 'threshold-based':
        scenario_names, var_names, scenario_definitions = get_threshold_based_scenario_names_vars_definitions()
    elif decision_rule == 'dynamic':
        scenario_names, var_names, scenario_definitions = get_dynamic_scenario_names_vars_definitions(
            wtp_values=wtp_values, dynamic_type=dynamic_type)
    else:
        raise ValueError('Invalid decision rule.')

    scenario_sim = ScenarioSimulator(model_settings=sets,
                                     scenario_names=scenario_names,
                                     variable_names=var_names,
                                     scenario_definitions=scenario_definitions)

    # get the seeds and probability weights
    seeds, weights = calib.get_seeds_lnl_probs('../SchoolClosure/summaries/open/calibration_summary.csv')

    scenario_sim.simulate(function_to_populate_model=M.build_school_closure_model,
                          num_of_sims=N,
                          seeds=seeds,
                          weights=weights,
                          sample_seeds_by_weights=False,
                          if_run_in_parallel=True,
                          print_summary_stats=True)

    # export results of the scenario analysis
    scenario_sim.export_results(filename='scenarios-{}.csv'.format(decision_rule))


if __name__ == "__main__":
    # simulate_scenarios(decision_rule='threshold-based')
    # simulate_scenarios(decision_rule='dynamic', dynamic_type='incd + cum incd', wtp_values=WTP_VALUES)
    simulate_scenarios(decision_rule='dynamic', dynamic_type='incd + delta incd', wtp_values=WTP_VALUES)
