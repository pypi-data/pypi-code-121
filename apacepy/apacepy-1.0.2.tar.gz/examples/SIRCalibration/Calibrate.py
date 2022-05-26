import apacepy.Calibration as calib
import deampy.ParameterEstimation as P

import examples.SIRCalibration.SIRCalibrationModel as M
from examples.SIRCalibration.SimulateMultiple import simulate_multi_trajectories

# To calibrate a simple SIR model when incidences should remain in a certain range

N_OF_CALIBRATION_ITERATIONS = 250    # total number of trajectories to simulate as part of calibration
N_OF_TRAJS_TO_USE_FOR_SIMULATION = 25   # number of trajectories with the highest likelihood to keep
N_OF_SAMPLES_TO_ESTIMATE_PARAMS = 200   # number of resampled parameters to estimate paramters

if __name__ == "__main__":

    # get model settings
    sets = M.get_model_settings()

    # --------- calibration ----------
    # calibrate the model
    calibration = calib.CalibrationWithRandomSampling(model_settings=sets)

    calibration.run(
        function_to_populate_model=M.build_SIR,
        num_of_iterations=N_OF_CALIBRATION_ITERATIONS,
        if_run_in_parallel=True)

    # save calibration results
    calibration.save_results(filename='summary/calibration_summary.csv')

    # ---------- parameter estimation -----------
    # calculate posterior distributions and plot figures
    estimator = P.ParameterAnalyzer()
    estimator.resample_param_values(csvfile_param_values_and_weights='summary/calibration_summary.csv',
                                    n=N_OF_SAMPLES_TO_ESTIMATE_PARAMS,
                                    weight_col=2,
                                    csvfile_resampled_params='summary/resampled_parameter_values.csv',
                                    sample_by_weight=True)
    param_list = ['R0', 'Infection duration', 'Recovery rate', 'Infectivity']
    print('\nPosterior distributions:')
    estimator.print_means_and_intervals(param_names=param_list)
    estimator.export_means_and_intervals(poster_file='summary/posteriors.csv', param_names=param_list)
    estimator.plot_pairwise(fig_filename='figures/posterior_figure.png', names=param_list)

    # ------- simulate the calibrated model ----------
    # get the seeds and probability weights
    seeds, weights = calib.get_seeds_lnl_probs('summary/calibration_summary.csv')

    # simulate the calibrated model with seeds weighted according to the probabilities
    simulate_multi_trajectories(n=N_OF_TRAJS_TO_USE_FOR_SIMULATION,
                                seeds=seeds,
                                weights=weights,
                                sample_seeds_by_weights=True,
                                figure_filename='Calibrated (weighted).png')

    # simulate the calibrated model with seeds with highest probabilities
    simulate_multi_trajectories(n=N_OF_TRAJS_TO_USE_FOR_SIMULATION,
                                seeds=seeds,
                                weights=weights,
                                sample_seeds_by_weights=False,
                                figure_filename='Calibrated (unweighted).png')
