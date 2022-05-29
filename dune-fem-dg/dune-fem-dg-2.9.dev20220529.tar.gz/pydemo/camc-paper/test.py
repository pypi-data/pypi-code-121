import os

from dune.alugrid import aluCubeGrid as aluGrid
from dune.grid import reader, cartesianDomain
from dune.fem.view import adaptiveLeafGridView as view
from dune.polygongrid import polygonGrid

import dune.fem
dune.fem.parameter.append({"fem.verboserank":0})

from advection_model import model
from evolve import evolve

Model = model(2)
order = 4
domain = (reader.dgf, "unitsquare.dgf")
gridView = view( aluGrid( domain, dimgrid=2 ) )
gridView.hierarchicalGrid.globalRefine(1)

os.makedirs("advection", exist_ok=True)

##################

parameters = {"femdg.limiter.indicator":"jump",
              "femdg.limiter.tolerance":0.25,
              "femdg.limiter.admissiblefunctions":1
             }

parameters["femdg.limiter.admissiblefunctions"]=3
parameters["femdg.limiter.tolerance"]=0.15
parameters["femdg.limiter.admissiblefunctions"]=3

##################

domain = (reader.dgf, "triangle.dgf")
gridView = view( polygonGrid( domain, dualGrid=True ) )
evolve(gridView, order, Model, "advection/poly",  limiter="MinMod",
                 maxLevel=-1, parameters=parameters, codeGen=True)
