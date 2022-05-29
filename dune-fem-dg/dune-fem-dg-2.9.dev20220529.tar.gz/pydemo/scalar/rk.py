from pprint import pprint
from dune.fem import parameter
from dune.femdg.rk import femdgStepper,\
        Heun,Midpoint,ssp2,ssp3,ExplSSP4_10
from dune.femdg.testing import run

# from scalar import shockTransport as problem
# from scalar import sinProblem as problem
# from scalar import sinTransportProblem as problem
# from scalar import sinAdvDiffProblem as problem
from scalar import pulse as problem
# from scalar import diffusivePulse as problem
# from scalar import burgersShock as problem

parameter.append({"fem.verboserank": 0})
parameters = {"dgadvectionflux.method": "LLF",
              "fem.solver.gmres.restart": 50,
              "dgdiffusionflux.method": "CDG2",      # CDG2, CDG, BR2, IP, NIPG, BO
              "dgdiffusionflux.theoryparameters": 1, # scaling with theory parameters
              "dgdiffusionflux.penalty": 0,
              "dgdiffusionflux.liftfactor": 1,
              "fem.ode.odesolver": "TBA",    # EX, IM, IMEX
              "fem.ode.order": "TBA",
              "fem.ode.verbose": "cfl",      # none, cfl, full
              "fem.ode.cflMax": 100,
              "fem.ode.cflincrease": 1.25,
              "fem.ode.miniterations": 0,
              "fem.ode.maxiterations": 10000}
limiter = None # "minmod"

results = {}

startLevels = [0,1,2]
polOrders   = [2,3]
methodsIm   = ["im2","midp","im3","sspIm2-1","sspIm3-9"]
methodsEx   = ["ex2","heun","ex3","ex4","ssp2-2","ssp2-9","ssp3-4","ssp3-9","ssp4-10"]
if limiter is None:
    methods = methodsEx + methodsIm
else:
    methods = methodsEx
# methods = ["ssp2-2","heun"]

for startLevel in startLevels:
    for polOrder in polOrders:
        res = {}
        for m in methods:
            print("#############################")
            print("### Using",startLevel,polOrder,m)
            print("#############################")
            if m == "ex2":
                parameters.update({'fem.ode.odesolver':'EX',"fem.ode.order":2})
                stepper = femdgStepper(parameters=parameters)
            elif m == "heun":
                stepper = Heun
            elif m == "ex3":
                parameters.update({'fem.ode.odesolver':'EX',"fem.ode.order":3})
                stepper = femdgStepper(parameters=parameters)
            elif m == "ex4":
                parameters.update({'fem.ode.odesolver':'EX',"fem.ode.order":4})
                stepper = femdgStepper(parameters=parameters)
            elif m == "im2":
                parameters.update({'fem.ode.odesolver':'IM',"fem.ode.order":2})
                stepper = femdgStepper(parameters=parameters)
            elif m == "im3":
                parameters.update({'fem.ode.odesolver':'IM',"fem.ode.order":3})
                stepper = femdgStepper(parameters=parameters)
            elif m == "midp":
                stepper = Midpoint
            elif m == "sspIm2-1":
                stepper = ssp2(1,explicit=False)
            elif m == "ssp2-2":
                stepper = ssp2(2)
            elif m == "ssp2-9":
                stepper = ssp2(9)
            elif m == "ssp3-4":
                stepper = ssp3(4)
            elif m == "ssp3-9":
                stepper = ssp3(9)
            elif m == "sspIm3-9":
                stepper = ssp3(9,explicit=False)
            elif m == "ssp4-10":
                stepper = ExplSSP4_10
            else:
                assert False
            uh,error = run(problem(), stepper,
                    startLevel=startLevel, polOrder=polOrder,
                    limiter=limiter,
                    primitive=None, saveStep=0.01, subsamp=0,
                    dt=None, parameters=parameters)
            res[m]=error
        pprint(res)
        results[(polOrder,startLevel)] = res

print("#############################")
print("### Restults")
print("#############################")
# pprint(results)
for keys,values in results.items():
    print(keys,":")
    for k,v in values.items():
        print(k,":",v)
