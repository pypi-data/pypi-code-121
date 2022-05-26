import apacepy.analysis.Trajectories as A

simOutcomes = A.SimOutcomeTrajectories(csv_directory='examples/SIR/trajectories/')

print('id:', simOutcomes.dictOfSimOutcomeTrajectories['Infectious|Incidence'].trajs[0].id)
print('simulation times:\n', simOutcomes.dictOfSimOutcomeTrajectories['Susceptible|Prevalence'].trajs[0].times)
print('observations:\n', simOutcomes.dictOfSimOutcomeTrajectories['Susceptible|Prevalence'].trajs[0].obss)

print('simulation periods:\n', simOutcomes.dictOfSimOutcomeTrajectories['Infectious|Incidence'].trajs[0].times)
print('observations:\n', simOutcomes.dictOfSimOutcomeTrajectories['Infectious|Incidence'].trajs[0].obss)

print('id:', simOutcomes.dictOfSimOutcomeTrajectories['Infectious|Incidence'].trajs[10].id)
print('times:\n', simOutcomes.dictOfSimOutcomeTrajectories['Infectious|Incidence'].trajs[10].times)
print('observations:\n', simOutcomes.dictOfSimOutcomeTrajectories['Infectious|Incidence'].trajs[10].obss)
