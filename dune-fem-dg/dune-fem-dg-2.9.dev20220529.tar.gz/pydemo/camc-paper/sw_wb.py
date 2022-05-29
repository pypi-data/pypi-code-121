import os

# from dune.alugrid import aluSimplexGrid as aluGrid
from dune.alugrid import aluCubeGrid as aluGrid
from dune.grid import reader, cartesianDomain
from dune.fem.view import adaptiveLeafGridView as view

from sw_model import modelWB as model

#################################

from dune.typeregistry import generateTypeName
from dune.generator import path
from dune.femdg import femDGOperator, femDGModels, advectionNumericalFlux
import evolve
def dgOperator(Model, space, limiter, parameters):
    models = femDGModels(Model,space)
    clsName,includes = generateTypeName("WB",models[1])
    flux = advectionNumericalFlux(clsName, [path(__file__)+"wb.hh"]+includes,
                                  models[1], additionalArgs=[Model.gravity])
    return femDGOperator(models, space, limiter=limiter, advectionFlux=flux)
evolve.femDGOperator = dgOperator

#################################

from evolve import evolve

order = 1
domain = cartesianDomain( [-1, 0], [2, 1], [240, 80] )
gridView = view( aluGrid( domain, dimgrid=2 ) )

os.makedirs("sw", exist_ok=True)

Model = model(gridView, g=1)
evolve(gridView, order, Model, "sw/wb",  limiter="MinMod",  maxLevel=-1)
