import examples.TB.TBModel as M
from apacepy.epidemic import EpiModel
from examples.TB.PlotTrajs import plot

# get model settings
sets = M.get_model_settings()
# make an (empty) epidemic model
model = EpiModel(id=0, settings=sets)
# populate the TB model
M.build_TB_model(model)

# simulate
model.simulate()
# print trajectories
model.export_trajectories(delete_existing_files=True)

# plot trajectories
plot(prev_multiplier=1,    # to show years on the x-axis of prevalence data
     incd_multiplier=1*sets.simulationOutputPeriod)     # to show years on the x-axis of incidence data
