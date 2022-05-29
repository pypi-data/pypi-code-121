from dune.fem import parameter
from dune.femdg.testing import run

from shallowwater import leVeque as problem
from shallowwater import bgModel

parameter.append({"fem.verboserank": -1})
# parameter.append("parameter")

primitive=lambda Model,uh: {"freesurface":Model.toPrim(uh)[0],
                            "topography":Model.topography}
parameters = {"fem.ode.odesolver": "EX",
              "fem.timeprovider.factor": 0.1,
              "fem.ode.order": 3,
              # "dgadvectionflux.method": "LLF",
              "femdg.limiter.admissiblefunctions": 1,
              "femdg.limiter.tolerance": 1,
              "femdg.limiter.epsilon": 1e-8}

run(problem(2,polOrder=2),
    limiter="none",polOrder=2,
    primitive=primitive, saveStep=0.1, subsamp=1,
    dt=None,threading=True,
    # grid="alucube",
    space="dgonb",
    parameters=parameters,
    modifyModel=bgModel)
