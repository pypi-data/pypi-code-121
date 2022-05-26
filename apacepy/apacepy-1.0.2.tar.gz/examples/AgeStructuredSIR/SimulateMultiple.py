import examples.AgeStructuredSIR.AgeStructSIRModel as M
from apacepy.multi_epidemics import MultiEpidemics
from examples.AgeStructuredSIR.PlotTrajs import plot


if __name__ == "__main__":

    # get model settings
    sets = M.get_model_settings()

    # build multiple epidemics
    multiModel = MultiEpidemics(model_settings=sets)

    multiModel.simulate(function_to_populate_model=M.build_age_structured_SIR_model,
                        n=25,
                        if_run_in_parallel=False)

    # save ids, seeds, runtime into a csv file
    multiModel.save_summary()

    # get summary statistics of runtime
    multiModel.print_summary_stats()

    # plot trajectories
    plot(prev_multiplier=52,  # to show weeks on the x-axis of prevalence data
         incd_multiplier=52*sets.simulationOutputPeriod)  # to show weeks on the x-axis of incidence data
