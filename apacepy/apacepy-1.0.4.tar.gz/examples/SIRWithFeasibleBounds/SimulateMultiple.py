import examples.SIRWithFeasibleBounds.SIRWithFeasibleBoundsModel as M
from apacepy.multi_epidemics import MultiEpidemics
from examples.SIRWithFeasibleBounds.PlotTrajs import plot


def simulate_multi_trajectories(n, seeds=None, weights=None, sample_seeds_by_weights=True, figure_filename='traj.png'):

    # get model settings
    sets = M.get_model_settings()

    # build multiple epidemics
    multi_model = MultiEpidemics(model_settings=sets)

    multi_model.simulate(function_to_populate_model=M.build_SIR_with_feasible_bounds,
                         n=n,
                         seeds=seeds,
                         weights=weights,
                         sample_seeds_by_weights=sample_seeds_by_weights,
                         if_run_in_parallel=True)

    # save ids, seeds, runtime,
    multi_model.save_summary()

    # get summary statistics of runtime,
    multi_model.print_summary_stats()

    # plot trajectories
    plot(prev_multiplier=52,  # to show weeks on the x-axis of prevalence data
         incd_multiplier=52*sets.simulationOutputPeriod,  # to show weeks on the x-axis of incidence data
         filename=figure_filename)


if __name__ == "__main__":

    simulate_multi_trajectories(n=25, figure_filename='Uncalibrated.png')
