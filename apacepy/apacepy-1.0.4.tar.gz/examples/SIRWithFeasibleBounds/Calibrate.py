import apacepy.Calibration as calib

import examples.SIRWithFeasibleBounds.SIRWithFeasibleBoundsModel as M
from examples.SIRWithFeasibleBounds.SimulateMultiple import simulate_multi_trajectories

# To calibrate a simple SIR model when incidences should remain in a certain range

N_OF_CALIB_SIMS = 25    # total number of trajectories to simulate as part of calibration
N_OF_SIMS = 10   # number of trajectories to simulate using the calibrated model


if __name__ == "__main__":

    # get model settings
    sets = M.get_model_settings()

    # calibrate the model
    calibration = calib.CalibrationWithRandomSampling(model_settings=sets)

    calibration.run(
        function_to_populate_model=M.build_SIR_with_feasible_bounds,
        num_of_iterations=N_OF_CALIB_SIMS,
        if_run_in_parallel=True)

    # save calibration results
    calibration.save_results(filename='summary/calibration_summary.csv')

    # get the seeds and probability weights
    seeds, weights = calib.get_seeds_lnl_probs('summary/calibration_summary.csv')

    # simulate the calibrated model
    simulate_multi_trajectories(n=N_OF_SIMS,
                                seeds=seeds,
                                weights=weights,
                                sample_seeds_by_weights=False,
                                figure_filename='Calibrated.png')
