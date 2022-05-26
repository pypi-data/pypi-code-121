from apacepy.ScenarioSimulation import ScenarioSimulator

import Plots as P
import examples.SchoolClosure.SchoolClosureModel as M

N_OF_SIMS = 5
RUN_IN_PARALLEL = True


def simulate_scenarios():

    # get model settings
    sets = M.SchoolClosureSettings()
    sets.exportTrajectories = False

    # names of the scenarios to evaluate
    scenario_names = ['No closure', 'Time-based closure', 'Threshold-base closure']
    # variable names (these correspond to the arguments of update_settings function of ModelSettings)
    var_names = ['School-closure', 'decision rule', 'time-on', 'time-off', 'threshold-on', 'threshold-off']
    # variable values
    # rows correspond to scenario names defined above, and columns correspond to variable names defined above
    scenario_definitions = [
        [True,      'time-based',       1000,   1000,   None,   None],
        [True,      'time-based',       2,      4,      None,   None],
        [True,      'threshold-based',  None,   None,   50,     10],
    ]
    scenario_sim = ScenarioSimulator(model_settings=sets,
                                     scenario_names=scenario_names,
                                     variable_names=var_names,
                                     scenario_definitions=scenario_definitions)

    scenario_sim.simulate(function_to_populate_model=M.build_school_closure_model,
                          num_of_sims=N_OF_SIMS,
                          if_run_in_parallel=RUN_IN_PARALLEL,
                          print_summary_stats=True)

    # export results of the scenario analysis
    scenario_sim.export_results()

    # plot the CEA figure and other analyses
    P.plot_cea(scenario_names=scenario_names)


if __name__ == "__main__":
    simulate_scenarios()
