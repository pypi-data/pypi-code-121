import examples.SIREconEval.SIREconEvalModel as M
from apacepy.epidemic import EpiModel
from examples.SIREconEval.PlotTrajs import plot

# get model settings
sets = M.get_model_settings()
# make an (empty) epidemic model
model = EpiModel(id=0, settings=sets)
# populate the SIR model
M.build_SIR_model(model)

# simulate
model.simulate()
# print trajectories
model.export_trajectories(delete_existing_files=True)
# print discounted outcomes
print(model.get_total_discounted_cost_and_health())

# plot trajectories
plot(prev_multiplier=52,    # to show weeks on the x-axis of prevalence data
     incd_multiplier=52*sets.simulationOutputPeriod)     # to show weeks on the x-axis of incidence data
