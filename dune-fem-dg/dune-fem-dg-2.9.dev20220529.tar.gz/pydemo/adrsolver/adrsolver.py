from os import environ
if environ.get('DUNE_PY_DIR') is None:
    import sys
    print("ERROR: Dune variables not set, source variables.sh first")
    sys.exit()

from dune.fem import parameter
from scheme import run

# from scalar import shockTransport as problem
# from scalar import sinProblem as problem
# from scalar import sinTransportProblem as problem
# from scalar import pulse as problem
from scalar import diffusivePulse as problem

parameter.append({"fem.verboserank": 0})

parameters = {"fem.ode.odesolver": "EX",   # EX, IM, IMEX
              "fem.ode.order": 3,
              "fem.ode.verbose": "none",      # none, cfl, full
              "fem.ode.cflincrease": 1.25,
              "fem.ode.miniterations": 35,
              "fem.ode.maxiterations": 100,
              "fem.timeprovider.factor": 0.25,
              "dgadvectionflux.method": "LLF",
              "fem.solver.gmres.restart": 50,
              "dgdiffusionflux.method": "CDG2",      # CDG2, CDG, BR2, IP, NIPG, BO
              "dgdiffusionflux.theoryparameters": 1, # scaling with theory parameters
              "dgdiffusionflux.penalty": 0,
              "dgdiffusionflux.liftfactor": 1}

try:
    run(*problem(),
            startLevel=0, polOrder=2, limiter=None,
            primitive=None, saveStep=0.01, subsamp=0,
            #dt=0.001,
            parameters=parameters)
except NameError:
    # from scalar import burgersShock as problem
    # from scalar import burgersVW as problem
    from scalar import burgersStationaryShock as problem
    parameters["fem.ode.odesolver"] = "EX"
    run(*problem(),
            startLevel=0, polOrder=2, limiter="default",
            primitive=None, saveStep=0.01, subsamp=2,
            dt=None,
            parameters=parameters)
