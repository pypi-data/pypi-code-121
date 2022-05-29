import dune.vem
import matplotlib
matplotlib.rc( 'image', cmap='jet' )
from matplotlib import pyplot
import math, pickle
from dune import create
from dune.grid import cartesianDomain, gridFunction
from dune.fem.plotting import plotPointData as plot
from dune.fem.function import integrate
from dune.fem import parameter
from dune.vem import voronoiCells

from ufl import *
import dune.ufl
dune.fem.parameter.append({"fem.verboserank": 0})

# use some run time parameters here to enable batch processesing
# the dump file should include the parameter values and the plot script
# should also use the parameters to determin input and output file names
order = 2
gridTypes = ["triangles","cartesian","quadrilaterals","voronoi","referenceTriangle"]
useGrid = 3 # 0..4
# note that the hessian of the reference element based basis
# function is not implemented for the 'quadrilaterals' grid

# Note: suboptimal laplace error for bubble (space is reduced to polorder=3 but could be 4 = ts+2
methods = [ ### "[space,scheme,spaceKwrags]"
            # ["lagrange","galerkin",{}, "Lagrange"],
            # ["vem","vem",{"testSpaces":[ [0],  [order-2], [order-1] ] }, "Bubble"],
            # ["vem","vem",{"testSpaces":[ [0],  [order-2], [order-3] ] }, "Serendipity"],
            # ["vem","vem",{"testSpaces":[ [-1], [order-1], [order-3] ] }, "Nc-Serendipity"],
            # ["vem","vem",{"conforming":True}, "conforming"],
            # ["vem","vem",{"conforming":False}, "non-conforming"],
            ["vem","vem",{"testSpaces":[ [0],  [order-3,order-2], [order-4] ] }, "C1-non-conforming"],
            ["vem","vem",{"testSpaces":[ [0],  [order-2,order-2], [order-2] ] }, "C1C0-conforming"],
            # ["bbdg","bbdg",{},"bbdg"],
   ]

uflSpace = dune.ufl.Space(2, dimRange=1)
x = SpatialCoordinate(uflSpace)
# exact = as_vector( [ 10 + x[0]*x[1] + x[0]**2*x[1] + x[1]**3 ] )
exact = as_vector( [x[0]*x[1] * cos(pi*x[0]*x[1])] )
# exact = as_vector( [x[0]*x[0]] )
def compute(grid, space, schemeName):
    # do the interpolation
    df = space.interpolate(exact,name="solution")
    info = {"linear_iterations":-1}
    # compute the error
    edf = exact-df
    err = [inner(edf,edf),
           inner(grad(edf),grad(edf)),
           inner(div(grad(edf)),div(grad(edf))),
           inner(grad(grad(edf)),grad(grad(edf)))
           ]
    errors = [ math.sqrt(e) for e in integrate(grid, err, order=8) ]
    if 0:
        plot(grad(df[0])[0],grid=grid,level=3)
        from dune.ufl import CoordWrapper
        import numpy
        df.interpolate([x[0]])
        for d in df.dofVector:
            print(d,end=", ")
        print()
        df.interpolate([x[1]])
        for d in df.dofVector:
            print(d,end=", ")
        print()
        for d in range(len(df.dofVector)):
            print(":::::::::::::::::::::::::::::")
            df.clear()
            df.dofVector[d] = 1
            for el in grid.elements:
                e = CoordWrapper(el,[0,0])
                print(numpy.round(df.ufl_evaluate(e,[0],[]),3),end="  ")
                e = CoordWrapper(el,[1,0])
                print(numpy.round(df.ufl_evaluate(e,[0],[]),3),end="  ")
                e = CoordWrapper(el,[0,1])
                print(numpy.round(df.ufl_evaluate(e,[0],[]),3),end="  |  ")

                e = CoordWrapper(el,[0.5,0])
                g = [ df.ufl_evaluate(e,[0],[0]), df.ufl_evaluate(e,[0],[1]) ]
                print(numpy.round(g[1],3),",",numpy.round(g[0],3),end="  ")
                e = CoordWrapper(el,[0,0.5])
                g = [ df.ufl_evaluate(e,[0],[0]), df.ufl_evaluate(e,[0],[1]) ]
                print(numpy.round(g[1],3),",",numpy.round(g[0],3),end="  ")
                e = CoordWrapper(el,[0.5,0.5])
                g = [ df.ufl_evaluate(e,[0],[0]), df.ufl_evaluate(e,[0],[1]) ]
                print(numpy.round(g[1],3),",",numpy.round(g[0],3),end="  ")
                print(";;;")
            # print(d)
            # print(":::::::::::::::::::::::::::::")
            # print("value")
            # df.plot(level=3)
            # print("gradient")
            # plot(grad(df[0])[0],grid=grid,level=3)
    return df, [ ["L^2",errors[0]],
                 ["H^1",errors[1]],
                 ["laplace",errors[2]],
                 ["H^2",errors[3]],
           ], info

results = []
for level in range(0,4):
    N = 2**(level+2)
    if useGrid == 0:
        constructor = cartesianDomain([-0.5,-0.5],[1,1],[N,N])
        polyGrid = create.grid("agglomerate", constructor, cubes=False )
    elif useGrid == 1:
        constructor = cartesianDomain([-0.5,-0.5],[1,1],[N,N])
        polyGrid = create.grid("agglomerate", constructor, cubes=True )
    elif useGrid == 2:
        # the following is a non affine cube grid, i.e., not parallelograms,
        cubeGrid = {"vertices": [ [-0.5,-0.5],[0   ,-0.5],[1,-0.5],
                                  [ 1,   0],  [1   , 1],
                                  [ 0,   1],  [-0.5, 1],
                                  [-0.5, 0],
                                  [0.25,0.25] ],
                    "cubes":  [ [0,1,7,8],[1,2,8,3],[8,3,5,4],[7,8,6,5] ]}
        polyGrid = create.grid("agglomerate", cubeGrid, cubes=True )
        polyGrid.hierarchicalGrid.globalRefine(level)
    elif useGrid == 3:
        constructor = cartesianDomain([0,0],[1,1],[N,N])
        polyGrid = create.grid("agglomerate",
                  voronoiCells(constructor,N*N,"voronoiseeds",load=True,show=False,lloyd=5) )
    elif useGrid == 4:
        if 1:
            # reference triangle
            refGrid = {"vertices": [ [0,0],[1,0],[0,1] ], "simplices":  [ [0,1,2] ]}
            # refGrid = {"vertices": [ [0,0],[1,0],[1,1],[0,1] ], "polygons": [ [0,1,2,3] ]}
            polyGrid = create.grid("agglomerate", refGrid, cubes=False )
        else:
            refGrid = {"vertices": [ [0,0],[1,0],[0,1],[1,1] ], "cubes": [ [0,1,2,3] ]}
            polyGrid = create.grid("agglomerate", refGrid, cubes=True )
        polyGrid.hierarchicalGrid.globalRefine(level)
    gridVidth = -1 # need something here
    @gridFunction(polyGrid, name="cells")
    def polygons(en,x):
        return polyGrid.hierarchicalGrid.agglomerate(en)
    # polygons.plot(colorbar="horizontal")

    # figCols = 4
    # figRows = len(methods)//figCols+1
    # fig = pyplot.figure(figsize=(10*figCols,10*figRows))
    # figPos = 100*figRows+10*figCols+1
    res = []
    for i,m in enumerate(methods):
        # dune.generator.setFlags(flags="-g",noChecks=True)
        space = create.space(m[0], polyGrid, order=order, dimRange=1, storage="istl", **m[2])
        # dune.generator.unsetFlags()
        dfs,errors,info = compute(polyGrid, space, m[1])
        print("method:(",m[0],m[2],")",
              "Size: ",space.size,
              *[e for e in errors],
              flush=True)
        # dfs.plot(figure=(fig,figPos+i),gridLines=None, colorbar="horizontal",level=3)
        # plot(grad(dfs)[0,0],grid=polyGrid,level=3,
        #      figure=(fig,figPos+i),gridLines=None, colorbar="horizontal")
        # plot(grad(grad(dfs))[0,0,0],grid=polyGrid,level=3,
        #      figure=(fig,figPos+i),gridLines=None, colorbar="horizontal")
        res += [ [m, gridVidth, space.size, errors] ]

    results += [res]
    pickle.dump(results,open('interpolation.dump','wb'))
print(results)
# pyplot.show()
