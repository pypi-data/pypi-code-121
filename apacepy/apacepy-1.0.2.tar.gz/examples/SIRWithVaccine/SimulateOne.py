import examples.SIRWithVaccine.SIRWithVaccineModel as M
from apacepy.epidemic import EpiModel
from examples.SIRWithVaccine.PlotTrajs import plot


def simulate(vaccination_on=False):

    # get model settings
    sets = M.get_model_settings(vaccination_on=vaccination_on)
    # make an (empty) epidemic model
    model = EpiModel(id=0, settings=sets)
    # populate the SIR model
    M.build_SIR_with_vaccine_model(model)

    # simulate
    model.simulate()
    # print trajectories
    model.export_trajectories(delete_existing_files=True)

    # plot trajectories
    plot(vaccination_on=vaccination_on,
         prev_multiplier=52,  # to show weeks on the x-axis of prevalence data
         incd_multiplier=52 * sets.simulationOutputPeriod)  # to show weeks on the x-axis of incidence data


simulate(vaccination_on=False)
simulate(vaccination_on=True)
