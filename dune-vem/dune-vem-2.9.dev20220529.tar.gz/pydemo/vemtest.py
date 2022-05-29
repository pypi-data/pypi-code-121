import dune.vem

import gc, sys, time
from memory_profiler import profile
from guppy import hpy

from loadMatlabMeshes import loadMatlabMeshes
import matplotlib
matplotlib.rc( 'image', cmap='jet' )
from matplotlib import pyplot
import math
from dune.grid import cartesianDomain, gridFunction
from dune.fem.plotting import plotPointData as plot
from dune.fem.function import integrate, discreteFunction
import dune.fem

from ufl import *
import dune.ufl

dune.fem.parameter.append({"fem.verboserank": 0})

# %% [markdown]
# We use a grid build up of voronoi cells around $50$ random points
# in the interval $[-\frac{1}{2},1]\times [-\frac{1}{2},1]$ using 100
# iterations of Lloyd's algorithm to improve the quality of the grid.

# %%

# %% [markdown]
# One can also use a standard simplex or cube grid, e.g.,
# polyGrid = dune.vem.polyGrid( cartesianDomain([-0.5,-0.5],[1,1],[10,10]), cubes=False)
#
# In general we can construct a `polygrid` by providing a dictionary with
# the `vertices` and the `polygons`. The `voronoiCells` function creates
# such a dictonary using random seeds to generate voronoi cells which are
# cut off using the provided `cartesianDomain`. The seeds can be
# provided as list of points as second argument:
# ```
# voronoiCells(constructor, towers, fileName=None, load=False):
# ```
# If a `fileName` is provided the seeds will be written to disc or if that
# file exists they will be loaded from that file if `load=True`,
# to make results reproducible.
#
# As an example an output of `voronoiCells(constructor,5)` is
# ```
# {'polygons': [ [4, 5, 2, 3], [ 8, 10,  9,  7], [7, 9, 1, 3, 4],
#                [11, 10,  8,  0], [8, 0, 6, 5, 4, 7] ],
#  'vertices': [ [ 0.438, 1.  ],    [ 1. , -0.5 ],
#                [-0.5, -0.5  ],    [ 0.923, -0.5 ],
#                [ 0.248,  0.2214], [-0.5,  0.3027],
#                [-0.5,  1. ],      [ 0.407,0.4896],
#                [ 0.414,  0.525],  [ 1.,  0.57228],
#                [ 1., 0.88293],    [ 1.,  1. ] ] }
# ```
#
# Let's take a look at the grid with the 50 polygons triangulated

# %%

# %% [markdown]
# The vem space is now setup in exactly the same way as usual but the type
# of space constructed is defined by the final argument which defines the
# moments used on the subentities of a given codimension. So
# `testSpaces=[-1,order-1,order-2]` means: use no vertex values (-1),
# order-1 moments on the edges and order-2 moments in the inside. So this
# gives us a non-conforming space for second order problems - while using
# `testSpaces=[0,order-2,order-2]` defines a conforming space.

# %%
space = dune.ufl.Space(2,1)
# space = dune.vem.vemSpace( polyGrid, order=order, dimRange=1)

# %% [markdown]
# Now we define the model starting with the exact solution:

# %%
x = SpatialCoordinate(space)
u = TrialFunction(space)
v = TestFunction(space)

exact = as_vector( [x[0]*x[1] * cos(pi*x[0]*x[1])] )

massCoeff = 1+sin(dot(x,x))       # factor for mass term
diffCoeff = 1-0.9*cos(dot(x,x))   # factor for diffusion term

a = (diffCoeff*inner(grad(u),grad(v)) + massCoeff*dot(u,v) ) * dx

# finally the right hand side and the boundary conditions
b = (-div(diffCoeff*grad(exact[0])) + massCoeff*exact[0] ) * v[0] * dx
dbc = [dune.ufl.DirichletBC(space, exact, i+1) for i in range(4)]

# %%
methods = lambda order:\
          [ ### "[legend,space,scheme,spaceKwargs,schemeKwargs]"
            ["lagrange",
             dune.fem.space.lagrange,dune.fem.scheme.galerkin,{},{}],
            ["dg",
             dune.fem.space.dgonb, dune.fem.scheme.dg,  {}, {"penalty":diffCoeff}],
            ["vem-conforming",
             dune.vem.vemSpace,    dune.vem.vemScheme,
                {"testSpaces":[0,order-2,order-2],  # conforming vem space
                 "basisChoice":3, "rotatedBB":False},
                {"gradStabilization":diffCoeff, "massStabilization":massCoeff}],
            ["vem-nonconforming",
             dune.vem.vemSpace,    dune.vem.vemScheme,
                 {"testSpaces":[-1,order-1,order-2],  # non-conforming vem space
                  "basisChoice":3, "rotatedBB":False},
                 {"gradStabilization":diffCoeff, "massStabilization":massCoeff}],
            ["bb-dg",
             dune.vem.bbdgSpace,   dune.vem.bbdgScheme, {}, {"penalty":diffCoeff}],
   ]


# %% [markdown]
# We now define a function to compute the solution and the $L^2,H^1$ error
# given a grid and a space

# %%
parameters = {"newton.linear.tolerance": 1e-12,
              "newton.linear.preconditioning.method": "jacobi",
              "penalty": 10*4**2,  # for the dg schemes
              "newton.linear.verbose": False,
              "newton.verbose": False,
              }
# @profile(precision=8)
def compute(grid, order, space, spaceArgs, schemeName,schemeArgs):
    space = space( grid, order=order, dimRange=1, storage="istl", **spaceArgs )
    df = space.interpolate([0],name="solution")
    scheme = schemeName( [a==b, *dbc], space, solver="cg", **schemeArgs,
                         parameters=parameters )
    info = scheme.solve(target=df)

    # compute the error
    edf = exact-df
    err = [inner(edf,edf),
           inner(grad(edf),grad(edf))]
    errors = [ math.sqrt(e) for e in integrate(grid, err, order=8) ]
    print("Solving:", info)
    return df, errors, info
def eoc(oldE,E):
    return [math.log(olde/e)/math.log(2) for olde,e in zip(oldE,E)]

# %% [markdown]
# Finally we iterate over the requested methods and solve the problems

# @profile(precision=8)
def linear():
    # mem = hpy()
    # meshes = [2500,10000,40000]
    meshes = [3,4] # [1...6]
    orders = [3,2]
    oldErr = []
    for nEl in meshes:
        print("==================================================",flush=True)
        # print(mem.heap(),flush=True)
        # polyGrid = dune.vem.polyGrid( dune.vem.voronoiCells([[-0.5,-0.5],[1,1]], nEl, lloyd=4) )
        polyGrid = dune.vem.polyGrid( loadMatlabMeshes("cvt",nEl), convex=True ) # importing my saved matlab meshes
        print("==================================================",flush=True)
        for j,order in enumerate(orders):
            if len(oldErr)>=j: oldErr += [len(methods(1))*[None]]
            for i,m in enumerate(methods(order)):
                if not m[1] == dune.vem.vemSpace: continue
                '''
                space, spaceArgs, schemeName,schemeArgs = m[1],m[3],m[2],m[4]
                print("--------------------------------------------------",flush=True)
                space = space( polyGrid, order=order, dimRange=1, storage="istl", **spaceArgs)
                print("--------------------------------------------------",flush=True)
                solution = space.interpolate([0],name="solution")
                scheme = schemeName( [a==b, *dbc], space, solver="cg", **schemeArgs,
                                     parameters=parameters )
                tic = time.perf_counter()
                for n in range(5):
                    space.update()
                toc = time.perf_counter()
                print(f"Update in {toc - tic:0.4f} seconds")
                tic = time.perf_counter()
                for n in range(5):
                    solution.clear()
                    info = scheme.solve(target=solution)
                    print("Solver:",info,flush=True)
                toc = time.perf_counter()
                print(f"Solve in {toc - tic:0.4f} seconds")
                tic = time.perf_counter()
                for n in range(5):
                    space.update()
                    solution.clear()
                    info = scheme.solve(target=solution)
                    print("Solver:",info,flush=True)
                toc = time.perf_counter()
                print(f"Solve/Update in {toc - tic:0.4f} seconds")
                continue
                '''
                _,errors,info = compute(polyGrid,order, m[1],m[3], m[2],m[4])
                print(i,nEl,j,"Error method (",m[0],polyGrid.size,order,"):",
                      "L^2: ", errors[0], "H^1: ", errors[1],
                      info["linear_iterations"], flush=True)
                if oldErr[j][i]:
                    print(j,i,"EOC method (",m[0],order,"):", eoc(oldErr[j][i],errors), flush=True)
                oldErr[j][i] = errors
                gc.collect()
    print("==================================================",flush=True)
    # print(mem.heap(),flush=True)
    print("==================================================",flush=True)

# @profile(precision=8)
def nonlinear():
    order = 3
    oldErr = None
    for nEl in [50,200]:
        polyGrid = dune.vem.polyGrid( dune.vem.voronoiCells([[-0.5,-0.5],[1,1]], nEl, lloyd=200) )
        space = dune.vem.vemSpace( polyGrid, order=order, dimRange=1, storage="istl", conforming=True,
                                   basisChoice=3, rotatedBB=False )
        u = TrialFunction(space)
        v = TestFunction(space)
        x = SpatialCoordinate(space)
        exact = as_vector ( [  (x[0] - x[0]*x[0] ) * (x[1] - x[1]*x[1] ) ] )
        Dcoeff = lambda u: 1.0 + u[0]**2
        a = (Dcoeff(u) * inner(grad(u), grad(v)) ) * dx
        b = -div( Dcoeff(exact) * grad(exact[0]) ) * v[0] * dx
        dbcs = [dune.ufl.DirichletBC(space, exact, i+1) for i in range(4)]
        scheme = dune.vem.vemScheme( [a==b, *dbcs], space, gradStabilization=Dcoeff(u),
                                     solver="cg", parameters=parameters)
        solution = space.interpolate([0], name="solution")
        info = scheme.solve(target=solution)
        edf = exact-solution
        errors = [ math.sqrt(e) for e in
                   integrate(polyGrid, [inner(edf,edf),inner(grad(edf),grad(edf))], order=8) ]
        print("non linear problem:", nEl, errors, flush=True )
        if oldErr:
            print("EOC non linear:", eoc(oldErr,errors), flush=True)
        oldErr = errors

# @profile(precision=8)
def bilapCompute(scheme,solution):
    solution.clear()
    # solution.interpolate(exact)
    info = scheme.solve(target=solution)
    # print("Solver:",info,flush=True)

@profile(precision=8)
def bilaplace():
    mem = hpy()
    order = 2
    oldErr = None
    ncC1testSpaces = [ [0], [order-3,order-2], [order-4] ]
    for nEl in [6]:
        #print("==================================================",flush=True)
        #print(mem.heap(),flush=True)
        #print("==================================================",flush=True)
        polyGrid = dune.vem.polyGrid( dune.vem.voronoiCells([[0,0],[1,1]], nEl, lloyd=2) )
        #print("setting up space",flush=True)
        space = dune.vem.vemSpace( polyGrid, order=order, dimRange=1, storage="istl",
                                   testSpaces=ncC1testSpaces,
                                   # basisChoice=3, rotatedBB=False
                                   )

        x = SpatialCoordinate(space)
        exact = as_vector( [sin(2*pi*x[0])**2*sin(2*pi*x[1])**2] )

        laplace = lambda w: div(grad(w))
        H = lambda w: grad(grad(w))
        u = TrialFunction(space)
        v = TestFunction(space)
        a = ( inner(H(u[0]),H(v[0])) ) * dx

        # finally the right hand side and the boundary conditions
        b = laplace(laplace(exact[0])) * v[0] * dx
        dbcs = [dune.ufl.DirichletBC(space, [0], i+1) for i in range(4)]

        solution = discreteFunction(space, name="solution")

        scheme = dune.vem.vemScheme( [a==b, *dbcs], space, hessStabilization=1,
                                     solver="cg", parameters=parameters )
        '''
        tic = time.perf_counter()
        for i in range(10):
            space.update()
        toc = time.perf_counter()
        print(f"Space update in {toc - tic:0.4f} seconds",flush=True)
        tic = time.perf_counter()
        for i in range(10):
            bilapCompute(scheme,solution)
        toc = time.perf_counter()
        print(f"Solve in {toc - tic:0.4f} seconds",flush=True)
        '''
        tic = time.perf_counter()
        for i in range(10):
            bilapCompute(scheme,solution)
        toc = time.perf_counter()
        #print(f"Computed in {toc - tic:0.4f} seconds",flush=True)

        edf = exact-solution
        errors = [ math.sqrt(e) for e in
                   integrate(polyGrid, [inner(edf,edf),
                                        inner(grad(edf),grad(edf)),
                                        inner(H(edf[0]),H(edf[0]))],
                                        order=8) ]
        #print("bi-laplace errors:", nEl, errors, flush=True)
        #if oldErr:
        #    print("EOC bi-laplace:", eoc(oldErr,errors), flush=True)
        oldErr = errors
        gc.collect()

    print("==================================================",flush=True)
    print(mem.heap(),flush=True)
    print("==================================================",flush=True)

for i in range(1):
    linear()
    gc.collect()
for i in range(5):
    nonlinear()
    gc.collect()
for i in range(25):
    bilaplace()
    gc.collect()
