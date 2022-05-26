import apacepy.Calibration as calib

import examples.SchoolClosure.SchoolClosureModel as M
from examples.SchoolClosure.SimulateMultiple import simulate

# To calibrate the school-closure model when incidence should remain in a certain range

N_OF_CALIB_SIMS = 500    # total number of trajectories to simulate as part of calibration
N_OF_SIMS = 50   # number of trajectories to simulate using the calibrated model


if __name__ == "__main__":

    # get model settings
    sets = M.SchoolClosureSettings()

    # calibrate the model
    calibration = calib.CalibrationWithRandomSampling(model_settings=sets)

    calibration.run(
        function_to_populate_model=M.build_school_closure_model,
        num_of_iterations=N_OF_CALIB_SIMS,
        if_run_in_parallel=True)

    # save calibration results
    calibration.save_results(filename='summaries/open/calibration_summary.csv')

    # get the seeds and probability weights
    seeds, weights = calib.get_seeds_lnl_probs('summaries/open/calibration_summary.csv')

    # simulate the calibrated model
    simulate(if_using_calibrated=True, n_of_sims=N_OF_SIMS)

