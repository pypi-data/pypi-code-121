import examples.TB.TBModel as M
from apacepy.multi_epidemics import MultiEpidemics
from examples.TB.PlotTrajs import plot

if __name__ == "__main__":

    # get model settings
    sets = M.get_model_settings()

    # build multiple epidemics
    multiModel = MultiEpidemics(model_settings=sets)

    # simulate all epidemic models
    multiModel.simulate(function_to_populate_model=M.build_TB_model,
                        n=50,
                        if_run_in_parallel=True)

    # save ids, seeds, runtime,
    multiModel.save_summary()

    # print summary statistics in the console,
    multiModel.print_summary_stats()

    # plot trajectories
    plot(prev_multiplier=1,  # to convert simulation time to week (the x-axis of prevalence data)
         incd_multiplier=sets.simulationOutputPeriod*1  # to convert simulation period to week
                                                         # (the x-axis of incidence data)
         )
