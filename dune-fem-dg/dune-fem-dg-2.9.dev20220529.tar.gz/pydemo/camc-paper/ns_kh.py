import os, sys
from argparse import ArgumentParser

# set number of threads to be used for thread parallel version
#os.environ['OMP_NUM_THREADS'] = '6'

parser = ArgumentParser()
parser.add_argument('level', type=int, help="max refinement level (negative means non-adaptive)")
parser.add_argument('--space', type=str, default="onb", help="onb|legendre|lagrange|equidistant|lobatto|gauss")
parser.add_argument('--stepper', type=str, default="ssp3",help="ssp2|ssp3|femdg (default: femdg)")
parser.add_argument('--order', type=int, default=4,help="[0,...,8] (default: 4)")
parser.add_argument('--grid',  type=str, default="cube", help="cube|simplex|naffine|poly (default: cube)")
parser.add_argument('--out',   type=int, default=100,help="number of output steps (default: 100)")
parser.add_argument('--mu',   type=float, default=0.001, help="viscosity parameter mu (default: 0.001)")
parser.add_argument
parser.parse_args()
try:
    args = parser.parse_args()
except SystemExit:
    sys.exit(0)
space = args.space
stepper = args.stepper
level = args.level
dim   = 2
grid  = args.grid
order = args.order
out   = args.out
mu    = args.mu

path = "ns_tmp/"
os.makedirs(path, exist_ok=True)
path = path+grid+str(dim)+str(abs(level))+"_"+space+"_"+str(mu).replace(".","")+"_"
if stepper != "femdg": path = path+stepper

from dune.grid import reader
from ns_model import model
Model = model(problem="KH",dim=2, mu=mu)

from dune.fem import parameter
parameter.append({"fem.verboserank":0})

if grid == "cube":
    from dune.alugrid import aluCubeGrid as grid
elif grid == "simplex":
    from dune.alugrid import aluSimplexGrid as grid
elif grid == "naffine":
    from dune.alugrid import aluCubeGrid as grid
    Model.domain = (reader.dgf, "shockvortex_naffine.dgf")
elif grid == "poly":
    try:
        from dune.polygongrid import polygonGrid as gridPoly
    except:
        print("dune-polygongrid not found, select other grid or install dune-polygongrid!")

    Model.domain = (reader.dgf, "shockvortex_poly.dgf")
    Model.boundary = Model.polyBoundary
    grid = lambda domain, dimgrid: gridPoly( Model.domain, dualGrid=True )

from dune.fem.view import adaptiveLeafGridView as view
from evolve import evolve

gridView = view( grid( Model.domain, dimgrid=dim ) )

parameters = {"fem.ode.verbose":"full",
              "fem.solver.newton.verbose":True,
              "fem.solver.newton.linear.verbose":True,
              "fem.solver.newton.linear.gmres.restart":100}


if level <= 0:
    if level<0:
        gridView.hierarchicalGrid.globalRefine(-level)
    evolve(gridView, order, Model, path,
           limiter=None,
           maxLevel=-1, outputs=out,
           parameters=parameters,
           space=space, stepper=stepper)
else:
    # gridView.hierarchicalGrid.globalRefine(level//2)
    evolve(gridView, order, Model, path+"_adapt",
           limiter=None,
           maxLevel=level, outputs=out,
           parameters=parameters,
           space=space, stepper=stepper)
