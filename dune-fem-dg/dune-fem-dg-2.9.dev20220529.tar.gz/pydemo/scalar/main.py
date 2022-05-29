from dune.fem import parameter
from dune.femdg.testing import run

# from scalar import shockTransport as problem
# from scalar import sinProblem as problem
# from scalar import sinTransportProblem as problem
# from scalar import sinAdvDiffProblem as problem
from scalar import pulse as problem
# from scalar import diffusivePulse as problem

parameter.append({"fem.verboserank": 0})

parameters = {"fem.ode.odesolver": "EX",   # EX, IM, IMEX
              "fem.ode.order": 3,
              "fem.ode.verbose": "cfl",      # none, cfl, full
              "fem.ode.cflMax": 100,
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

parameters['fem.ode.odesolver'] = 'EX'
uh,errorEx = run(problem(),
        startLevel=0, polOrder=2, limiter=None,
        primitive=None, saveStep=0.01, subsamp=0,
        dt=None,
        parameters=parameters)
parameters['fem.ode.odesolver'] = 'IM'
uh,errorIm = run(problem(),
        startLevel=0, polOrder=2, limiter=None,
        primitive=None, saveStep=0.01, subsamp=0,
        dt=None,
        parameters=parameters)
parameters['fem.ode.odesolver'] = 'IMEX'
uh,errorImex = run(problem(),
        startLevel=0, polOrder=2, limiter=None,
        primitive=None, saveStep=0.01, subsamp=0,
        dt=None,
        parameters=parameters)
print(errorEx,errorIm,errorImex)
