import os, math

# from dune.alugrid import aluSimplexGrid as aluGrid
from dune.alugrid import aluCubeGrid as aluGrid
from dune.grid import reader, cartesianDomain
from dune.fem.view import adaptiveLeafGridView as view

from chemical_model import model
from evolve import evolve

order = 2
domain = cartesianDomain( [0, 0], [2*math.pi, 2*math.pi], [50, 50] )
gridView = view( aluGrid( domain, dimgrid=2 ) )

os.makedirs("chemical", exist_ok=True)

Model = model(gridView,order=order)
# evolve(gridView, order, Model, "chemical/minmod",  limiter="scaling", codegen=False, outputs=10)
evolve(gridView, order, Model, "chemical/codegen",  limiter="scaling", codegen=True, outputs=10)
