import os, sys
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('level', type=int, help="max refinement level (negative means non-adaptive)")
parser.add_argument('--space', type=str, default="onb",
        help="onb|legendre|lagrange|equidistant|lobatto|gauss")
parser.add_argument('--stepper', type=str, default="ssp3",help="ssp2|ssp3|femdg (default: ssp3)")
parser.add_argument('--dim',   type=int, default=2, help="2|3 (default: 2)")
parser.add_argument('--order', type=int, default=4,help="[0,...,8] (default: 4)")
parser.add_argument('--grid',  type=str, default="cube", help="cube|simplex|naffine|poly (default: cube)")
parser.add_argument('--out',   type=int, default=50,help="number of output steps (default: 50)")
parser.add_argument('--modal', type=str, default='',help="switch on modal limiter")
parser.add_argument
parser.parse_args()
try:
    args = parser.parse_args()
except SystemExit:
    sys.exit(0)
space = args.space
stepper = args.stepper
level = args.level
dim   = args.dim
grid  = args.grid
order = args.order
out   = args.out
modal = args.modal

limiter="minmod"
modalComponent=None
if not modal == '':
    limiter = "modal"
    modalComponent = modal

path = "euler_kh/"
os.makedirs(path, exist_ok=True)
path = path+grid+str(dim)+str(abs(level))+limiter+modal+"_"+space
path = path + "_tol02"
if stepper != "femdg": path = path+stepper

from dune.grid import reader
from euler_model import model
Model = model(problem="KH",dim=dim)

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
    grid = lambda domain, dimgrid: gridPoly( Model.domain, dualGrid=True )

from dune.fem.view import adaptiveLeafGridView as view
from evolve import evolve

import time

gridView = view( grid( Model.domain, dimgrid=dim ) )

parameters = {}
#parameters["femdg.limiter.tolerance"]=0.2
#parameters["fem.timeprovider.factor"]=0.4

if level <= 0:
    if level<0:
        gridView.hierarchicalGrid.globalRefine(-level)
    evolve(gridView, order, Model, path,
           limiter=limiter,modalComponent=modalComponent,
           maxLevel=-1, outputs=out,
           parameters=parameters,
           space=space, stepper=stepper)
else:
    evolve(gridView, order, Model, path+"_adapt",
           limiter=limiter,modalComponent=modalComponent,
           maxLevel=level, outputs=out,
           parameters=parameters,
           space=space, stepper=stepper)
