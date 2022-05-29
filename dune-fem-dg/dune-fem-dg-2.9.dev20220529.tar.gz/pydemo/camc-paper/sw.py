import os

# from dune.alugrid import aluSimplexGrid as aluGrid
from dune.alugrid import aluCubeGrid as aluGrid
from dune.grid import reader, cartesianDomain
from dune.fem.view import adaptiveLeafGridView as view

from dune.typeregistry import generateTypeName
from dune.generator import path
from dune.femdg import femDGOperator, femDGModels, advectionNumericalFlux

import evolve

from sw_model import model

order = 1
domain = cartesianDomain( [0, 0], [1, 0.01], [120, 1] )
gridView = view( aluGrid( domain, dimgrid=2 ) )

os.makedirs("sw", exist_ok=True)

parameters = {"femdg.limiter.indicator":"jump",
              "femdg.limiter.tolerance":0.25,
              "femdg.limiter.admissiblefunctions":3
             }

#Model = model(gridView, order, g=1, problem="LeVeque", wb=False)
Model = model(gridView, order, g=1, problem="dambreak", wb=False)
evolve.evolve(gridView, order, Model, "sw/minmod",  limiter="MinMod", maxLevel=-1, parameters=parameters)


################################################

#def dgOperator(Model, space, limiter, codegen=True, threading=False, defaultQuadrature=True, parameters=parameters):
#    models = femDGModels(Model,space)
#    clsName,includes = generateTypeName("WB",models[1])
#    flux = advectionNumericalFlux(clsName, [path(__file__)+"wb.hh"]+includes,
#                                  models[1], additionalArgs=[Model.gravity])
#    return femDGOperator(models, space, limiter=None, codegen=codegen, advectionFlux=flux)
#evolve.femDGOperator = dgOperator

#Model = model(gridView, order, g=1, problem="LeVeque", wb=True)
#evolve.evolve(gridView, order, Model, "sw/wb_minmod",  limiter="MinMod", maxLevel=-1, parameters=parameters)
