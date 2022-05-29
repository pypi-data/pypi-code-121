from dune.fem import parameter
from dune.femdg.testing import run

import scalar, shallowWater, euler

parameter.append({"fem.verboserank": -1})

parameters = {"fem.ode.odesolver": "EX",   # EX, IM, IMEX
              "fem.ode.order": 3,
              "fem.ode.verbose": "none",      # none, cfl, full
              "fem.ode.cflincrease": 1.25,
              "fem.ode.miniterations": 35,
              "fem.ode.maxiterations": 100,
              "fem.timeprovider.factor": 0.45,
              "dgadvectionflux.method": "LLF",
              "fem.solver.gmres.restart": 50,
              "dgdiffusionflux.method": "CDG2",      # CDG2, CDG, BR2, IP, NIPG, BO
              "dgdiffusionflux.theoryparameters": 1, # scaling with theory parameters
              "dgdiffusionflux.penalty": 0,
              "dgdiffusionflux.liftfactor": 1}

for p in shallowWater.problems + euler.problems:
    run(*p(), startLevel=0, polOrder=2, limiter="default",
              primitive=None, saveStep=None, subsamp=0,
              dt=None,threading=True,grid="alucube",
              parameters=parameters)
    # run(*p(), startLevel=0, polOrder=2, limiter="default",
    #           primitive=None, saveStep=None, subsamp=0,
    #           dt=None,threading=True,grid="alusimplex",
    #           parameters=parameters)

parameters["fem.ode.odesolver"] = "IM"
for p in scalar.problems:
    run(p(), startLevel=0, polOrder=2, limiter=None,
              primitive=None, saveStep=None, subsamp=0,
              dt=None,threading=True,grid="alucube",
              parameters=parameters)
    run(p(), startLevel=0, polOrder=0, limiter=None,
              primitive=None, saveStep=None, subsamp=0,
              dt=None,threading=True,grid="yasp",
              parameters=parameters)
