import apacepy.Calibration as calib

import examples.SchoolClosure.Plots as P
import examples.SchoolClosure.SchoolClosureModel as M
from apacepy.multi_epidemics import MultiEpidemics

N_OF_SIMS = 50   # number of trajectories to simulate using the calibrated model
IF_RUN_IN_PARALLEL = True
IF_USING_CALIBRATED = True
WTP = 0.02


def simulate(if_using_calibrated=None, schools_closed=False, decision_rule='time-based', dynamic_type=None,
             n_of_sims=None):
    """
    :param if_using_calibrated: (bool) if using the calibrated model 
    :param schools_closed: (bool) False if schools are never closed
    :param decision_rule: (string) 'time-based', 'threshold-based', or 'dynamic'
    :param dynamic_type: 'cum incd' for using cumulative incidence as feature
         'incd + cum incd' for using incidence and cumulative incidence as feature
         'incd + pd status' for using incidence and the status of physical distancing intervention
         as feature
    :param n_of_sims:
    """

    # get model settings
    sets = M.SchoolClosureSettings()
    sets.update_settings(schools_closed=schools_closed, decision_rule=decision_rule,
                         time_on=2, time_off=4, threshold_on=200, threshold_off=200,
                         dynamic_type=dynamic_type, wtp=WTP)

    # build multiple epidemics
    multi_model = MultiEpidemics(model_settings=sets)

    # if using the calibrated model
    if_using_calibrated = IF_USING_CALIBRATED if if_using_calibrated is None else if_using_calibrated
    if if_using_calibrated:
        # get the seeds and probability weights
        seeds, weights = calib.get_seeds_lnl_probs('summaries/open/calibration_summary.csv')
    else:
        seeds, weights = None, None

    n = N_OF_SIMS if n_of_sims is None else n_of_sims
    multi_model.simulate(function_to_populate_model=M.build_school_closure_model,
                         n=n,
                         seeds=seeds,
                         weights=weights,
                         sample_seeds_by_weights=False,
                         if_run_in_parallel=IF_RUN_IN_PARALLEL)

    # save ids, seeds, runtime into a csv file
    multi_model.save_summary()

    # get summary statistics of runtime
    multi_model.print_summary_stats(wtp=WTP, health_multiplier=1, cost_multiplier=52)

    # plot trajectories
    P.plot_trajs(schools_closed=schools_closed,
                 decision_rule=decision_rule,
                 prev_multiplier=52,  # to show weeks on the x-axis of prevalence data
                 incd_multiplier=52*sets.simulationOutputPeriod,
                 obs_incd_multiplier=52*sets.observationPeriod)  # to show weeks on the x-axis of incidence data


if __name__ == "__main__":
    simulate(schools_closed=False)
    # simulate(schools_closed=True, decision_rule='time-based')
    simulate(schools_closed=True, decision_rule='threshold-based')

    simulate(schools_closed=True, decision_rule='dynamic', dynamic_type='cum incd')
    # simulate(schools_closed=True, decision_rule='dynamic', dynamic_type='incd + cum incd')
    # simulate(schools_closed=True, decision_rule='dynamic', dynamic_type='incd + closure status')


