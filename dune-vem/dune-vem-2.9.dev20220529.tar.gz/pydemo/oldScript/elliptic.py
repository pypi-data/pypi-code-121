from __future__ import print_function

import math, sys, pickle

from ufl import *
import dune.ufl

from dune import create
from dune.grid import cartesianDomain, gridFunction
from dune.fem import parameter
from dune.fem.operator import linear
from dune.vem import voronoiCells

dimRange = 2
start    = 3
# polOrder, endEoc = 1,8
polOrder, endEoc = 2,8
# polOrder, endEoc = 3,6
# polOrder, endEoc = 4,5
# polOrder, endEoc = 5,4
# polOrder, endEoc = 6,4 # not working
methods = [ ### "[space,scheme,spaceKwrags]"
            ["lagrange","h1",{}],
            ["vem","vem",{"conforming":True}],
            ["vem","vem",{"conforming":False}],
            ["bbdg","bbdg",{}],
            # ["dgonb","dg",{}], # dg does not converge
   ]
parameters = {"newton.linear.tolerance": 1e-12,
              "newton.linear.verbose":True,
              "newton.tolerance": 1e-10,
              "newton.maxiterations": 10, # should finish in 1 for linear
              "newton.maxlinesearchiterations":50,
              "newton.verbose": False,
              "newton.linear.preconditioning.method": "amg-ilu",
              "penalty": 8*polOrder*polOrder
              }



dune.fem.parameter.append({"fem.verboserank": 0})

def plot(grid, solution):
    try:
        from matplotlib import pyplot
        from numpy import amin, amax, linspace

        triangulation = grid.triangulation(4)
        data = solution.pointData(4)

        levels = linspace(amin(data[:,0]), amax(data[:,0]), 256)

        pyplot.gca().set_aspect('equal')
        pyplot.triplot(grid.triangulation(), antialiased=True, linewidth=0.2, color='black')
        pyplot.tricontourf(triangulation, data[:,0], cmap=pyplot.cm.rainbow, levels=levels)
        pyplot.show()
    except ImportError:
        pass

def error(grid, df, interp, exact):
    edf = exact-df
    ein = exact-interp
    errors = create.function("ufl", grid, "error", 5,
            [ dot(edf,edf), dot(ein,ein),
              inner(grad(edf),grad(edf)), inner(grad(ein),grad(ein))
            ] ).integrate()
    return [ math.sqrt(e) for e in errors ]

h1errors  = []
l2errors  = []
spaceSize = []

def solve(grid,model,exact,space,scheme,spaceKwargs,order):
    print("SOLVING: ",space,scheme,spaceKwargs,flush=True)
    spc = create.space(space, grid, dimRange=dimRange, order=order,
            storage="istl", **spaceKwargs)
    name = space + "_".join(['']+[str(v) for v in spaceKwargs.values()])
    interpol = spc.interpolate( exact, "interpol_"+name )
    scheme = create.scheme(scheme, model, spc,
                solver="cg",
                parameters=parameters)
    df = spc.interpolate([0,]*dimRange,name=name)
    # info = {"linear_iterations":-1,"iterations":-1}
    info = scheme.solve(target=df)

    # import pickle,sys
    # linOp = linear(scheme)
    # scheme.jacobian(df,linOp)
    # pickle.dump([linOp.as_numpy,df.as_numpy], open( "dump"+str(dimRange), "wb" ) )
    # sys.exit(0)

    errors = error(grid,df,interpol,exact)
    print("Computed",name," size:",spc.size,
          "L^2 (s,i):", [errors[0],errors[1]],
          "H^1 (s,i):", [errors[2],errors[3]],
          "linear and Newton iterations:",
          info["linear_iterations"], info["iterations"],flush=True)
    global h1errors, l2errors, spaceSize
    l2errors  += [errors[0],errors[1]]
    h1errors  += [errors[2],errors[3]]
    spaceSize += [spc.size]
    return interpol, df

def compute(grid):
    uflSpace = dune.ufl.Space((grid.dimGrid, grid.dimWorld), dimRange, field="double")
    u = TrialFunction(uflSpace)
    v = TestFunction(uflSpace)
    x = SpatialCoordinate(uflSpace.cell())
    if True:
        ##### problem 1
        ### trivial Neuman bc
        exact  = as_vector([
                  cos(r*pi*x[0])*cos(r*pi*x[1]) for r in range(2,dimRange+2)
                ])
        #### zero boundary conditions
        exact *= x[0]*x[1]*(2-x[0])*(2-x[1])
        #### non zero and non trivial Neuman boundary conditions
        exact += as_vector([
                    sin(r*x[0]*r*x[1]) for r in range(1,dimRange+1)
                 ])
        H = lambda w: grad(grad(w))
        laplace = lambda w: H(w)[0,0] + H(w)[1,1]
        a = (inner(grad(u),grad(v))) * dx
        b = sum( [( -laplace(exact[r]) ) * v[r] * dx
                 for r in range(dimRange)] )
        # a += inner(u,v) * dx
        # b += inner(exact,v) * dx
    else:
        ##### problem 2: dummy quasilinear problem:
        exact = as_vector ( [  (x[0] - x[0]*x[0] ) * (x[1] - x[1]*x[1] ) ] )
        Dcoeff = lambda u: 1.0 + u[0]**2
        a = (Dcoeff(u)* inner(grad(u), grad(v)) ) * dx
        b = -div( Dcoeff(u) * grad(exact[0]) ) * v[0] * dx
    dbc = [dune.ufl.DirichletBC(uflSpace, exact, i+1) for i in range(4)]
    model = create.model("elliptic", grid, a==b, *dbc)
    dfs = []
    for m in methods:
        dfs += solve(grid,model,exact,*m,order=polOrder)

    @gridFunction(grid, name="cells")
    def polygons(en,x):
        return grid.hierarchicalGrid.agglomerate(en)
    grid.writeVTK(grid.hierarchicalGrid.agglomerate.suffix,
        pointdata=dfs, celldata=[polygons] )
    grid.writeVTK("s"+grid.hierarchicalGrid.agglomerate.suffix,subsampling=polOrder-1,
        pointdata=dfs, celldata=[polygons] )


for i in range(endEoc-start):
    print("*******************************************************")
    n = 2**(i+start)
    N = 2*n
    print("Test: ",n,N)
    constructor = cartesianDomain([0,0],[1,1],[N,N])
    # polyGrid = create.grid("agglomerate",constructor,[n,n])
    # polyGrid = create.grid("agglomerate",constructor,n*n)
    polyGrid = create.grid("agglomerate", voronoiCells(constructor,n*n,"voronoiseeds",True) )
    # polyGrid = create.grid("agglomerate",constructor)
    compute(polyGrid)
    if i>0:
        l = len(methods)
        for j in range(2*l):
            try:
                l2eoc = math.log( l2errors[2*l*i+j]/l2errors[2*l*(i-1)+j] ) / math.log(0.5)
            except ValueError:
                l2eoc = -1
            try:
                h1eoc = math.log( h1errors[2*l*i+j]/h1errors[2*l*(i-1)+j] ) / math.log(0.5)
            except ValueError:
                h1eoc = -1
            print("EOC",methods[int(j/2)][0],j,l2eoc,h1eoc)
    with open("errors_p"+str(polOrder)+".dump", 'wb') as f:
        pickle.dump([methods,spaceSize,l2errors,h1errors], f)
    print("*******************************************************")
