import os, sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('level', type=int)
parser.add_argument('--space', type=str, default="onb")
parser.add_argument('--dim',   type=int, default=2)
parser.add_argument('--order', type=int, default=4)
parser.add_argument('--grid',  type=str, default="cube")
parser.add_argument('--out',   type=int, default=50)
parser.add_argument
parser.parse_args()
try:
    args = parser.parse_args()
except SystemExit:
    sys.exit(0)
space = args.space
level = args.level
dim   = args.dim
grid  = args.grid
order = args.order
out   = args.out

path = "euler_sb/"
os.makedirs(path, exist_ok=True)
path = path+grid+str(dim)+str(abs(level))+"_"+space

from dune.grid import reader
from euler_model import model
Model = model(problem="SB",dim=dim)

if grid == "cube":
    from dune.alugrid import aluCubeGrid as grid
elif grid == "simplex":
    from dune.alugrid import aluSimplexGrid as grid
elif grid == "poly":
    from dune.polygongrid import polygonGrid as gridPoly
    Model.domain = (reader.dgf, "shockvortex_poly.dgf")
    grid = lambda domain, dimgrid: gridPoly( Model.domain, dualGrid=True )
    Model.boundary  = {1: lambda t,x,U,n:
            conditional(x[0]<-0.399,
                        Model.F_c(t,x,U)*n, noFlowFlux(U,n))
                      }

from dune.fem.view import adaptiveLeafGridView as view
from evolve import evolve

parameters = {"femdg.limiter.indicator":"jump",
              "femdg.limiter.tolerance":0.5,
              "femdg.limiter.admissiblefunctions":"default"
             }

gridView = view( grid( Model.domain, dimgrid=dim ) )

if level <= 0:
    if level<0:
        gridView.hierarchicalGrid.globalRefine(-level)
    evolve(gridView, order, Model, path,
           maxLevel=-1, parameters=parameters, outputs=out,
           space=space)
else:
    evolve(gridView, order, Model, path+"_adapt",
           maxLevel=level, parameters=parameters, outputs=out,
           space=space)
