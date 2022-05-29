import dune.vem
import matplotlib
matplotlib.rc( 'image', cmap='jet' )
from matplotlib import pyplot
import math
from dune import create
from dune.grid import cartesianDomain, gridFunction
from dune.fem.plotting import plotPointData as plot
from dune.fem.function import integrate, discreteFunction
from dune.fem import parameter
from dune.vem import voronoiCells
from dune.fem.operator import linear as linearOperator
from scipy.sparse.linalg import spsolve

from ufl import *
import dune.ufl

maxLevel     = 5
order        = 3

dune.fem.parameter.append({"fem.verboserank": 0})

methods = [ ### "[space,scheme,spaceKwrags]"
            ["vem","vem",{"testSpaces":[ [0],  [order-3,order-2], [order-4] ] }, "C1-non-conforming"],
            # ["vem","vem",{"testSpaces":[ [0],  [order-2,order-2], [order-2] ] }, "C1C0-conforming"],
            # ["vem","vem",{"testSpaces":[ [-1], [order-1,-1], [order-2] ] },   "C0-non-conforming"],
   ]
parameters = {"newton.linear.tolerance": 1e-8,
              "newton.tolerance": 5e-6,
              "newton.linear.preconditioning.method": "jacobi",
              "newton.lineSearch": "simple",
              "penalty": 40,  # for the bbdg scheme
              "newton.linear.verbose": False,
              "newton.verbose": True
              }


def compute(grid, s, schemeName):
    dt = 4e-4
    space = create.space(s[0], polyGrid, order=order, **s[1])
    t   = dune.ufl.Constant(0,"time")

    x   = SpatialCoordinate(space)
    initial = sin(2*pi*x[0])**2*sin(2*pi*x[1])**2

    # Wilmore functional W(psi)
    psi = Coefficient(space)
    Q = lambda p: 1+inner(p,p)
    E = lambda p: 1/Q(p)**0.25 * ( Identity(2) - outer(p,p)/Q(p) )
    Wint = 1/2*inner( E(grad(psi)),grad(grad(psi)) )**2
    W = Wint * dx

    # variation bilinear form
    phi = TestFunction(space)
    a   = derivative(W,psi,phi)

    # third order time stepping (Gauss radau collocation)
    tau = dune.ufl.Constant(0,"dt")
    df  = discreteFunction(space, name="solution") # main solution
    # space for time stepping (df=U^n, U[0]=intermediate, U[1]=U^{n+1}
    rkSpace = create.space(s[0], polyGrid, order=order, dimRange=2, **s[1])
    U       = TrialFunction(rkSpace)
    V       = TestFunction(rkSpace)
    dfs     = [  df,   U[0],  U[1]  ]
    factors = [ [-2,  3./2., 1./2.] ,
                [ 2, -9./2., 5./2.] ]
    dtForm = lambda w,u,v: inner(w/Q(u),v)*dx
    rkForm  = sum(f*dtForm(u,U[i],V[i]) for i in range(2) for u,f in zip(dfs,factors[i]))
    rkForm += tau*sum(replace(a,{psi:U[i],phi:V[i]}) for i in range(2))

    dbc = [dune.ufl.DirichletBC(rkSpace, rkSpace.dimRange*[0], i+1) for i in range(4)]
    biLaplaceCoeff = [dt,dt]
    diffCoeff      = [0,0]
    massCoeff      = [1,1] # 1/Q(U[i]) for i in range(2)]

    print("# solving: ",s, "size",space.size, "parameters:(", biLaplaceCoeff,",",diffCoeff,",",massCoeff,")")

    scheme = create.scheme(schemeName,
                        [rkForm == 0, *dbc], # space, # this gives is a compiler error
                        solver=("suitesparse","umfpack"),
                        hessStabilization=biLaplaceCoeff,
                        gradStabilization=diffCoeff,
                        massStabilization=massCoeff,
                        parameters=parameters)
    df.interpolate(initial)
    energy = integrate(grid,replace(Wint,{psi:df}),order=5)
    vtk = grid.sequencedVTK("voro", pointdata=[df],subsampling=2)
    t.value = 0
    tau.value = dt
    count = 0
    info = None
    # tmp = discreteFunction(rkSpace, name="rk")
    tmp = rkSpace.interpolate([initial,initial], name="rk")
    while t.value < 0.01:
        count += 1
        if count % 1 == 0:
            energy = integrate(grid,replace(Wint,{psi:df}),order=5)
            vtk()
        print("[",count,"]",t.value,energy,tau.value,info,flush=True)
        info = scheme.solve(target=tmp)
        t.value += tau
        df.interpolate(tmp[1])
    return df

for level in range(1,2): # maxLevel): # 2,3
    constructor = cartesianDomain([0,0],[1,1],[20*2**level,20*2**level])
    polyGrid = create.grid("agglomerate", constructor, cubes=False )
    # polyGrid = create.grid("agglomerate", voronoiCells(constructor,400*2**level*2**level,"voronoiseeds",load=True,show=False,lloyd=5) )
    @gridFunction(polyGrid, name="cells")
    def polygons(en,x):
        return polyGrid.hierarchicalGrid.agglomerate(en)
    # polygons.plot(colorbar="horizontal")
    for i,m in enumerate(methods):
        dfs = compute(polyGrid, [m[0], m[2]], m[1])
        print("[",level,"]","method:(",m[0],m[2],")",
              "Grid-Size: ",polyGrid.size(0), flush=True)
