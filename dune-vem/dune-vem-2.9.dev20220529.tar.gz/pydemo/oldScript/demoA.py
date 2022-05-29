# <markdowncell>
# # Demonstration notebook for the DUNE-VEM module
# This module is based on DUNE-FEM # (https://www.dune-project.org/modules/dune-fem)
# and provides a Python frontend based on the new Python extension to DUNE
# (https://dune-project.org/modules/dune-python)
#
# ## Laplace problem
#
# We first consider a simple Laplace problem with Dirichlet boundary conditions
# \begin{align*}
#   -\Delta u &= f, && \text{in } \Omega, \\
#           u &= g, && \text{on } \partial\Omega,
# \end{align*}
# with $\Omega=[-\frac{1}{2},1]^2$ and choosing the forcing and the boundary conditions
# so that the exact solution is equal to
# \begin{align*}
#   u(x,y) &= xy\cos(\pi xy)
# \end{align*}

# First some setup code:
# <codecell>
try:
    get_ipython().magic(u'matplotlib nbagg')
    import matplotlib
    matplotlib.rc( 'image', cmap='rainbow' )
except:
    pass
import math
from dune import create
from dune.grid import cartesianDomain, gridFunction
from dune.fem.plotting import plotPointData as plot
from dune.fem.function import integrate
from dune.fem import parameter
from dune.vem import voronoiCells

from ufl import *
import dune.ufl

dune.fem.parameter.append({"fem.verboserank": 0})

# <markdowncell>
# we can compare different method, e.g., a lagrange space (on the # subtriangulation),
# a bounding box dg space and a conforming/non conforming VEM space

# <codecell>
methods = [ ### "[space,scheme,spaceKwrags]"
            ["lagrange","h1",{}],
            ["vem","vem",{"conforming":True}],
            ["vem","vem",{"conforming":False}],
            ["bbdg","bbdg",{}],
   ]
parameters = {"newton.linear.tolerance": 1e-12,
              "newton.linear.preconditioning.method": "ilu",
              "penalty": 40,  # for the bbdg scheme
              "newton.linear.verbose": True,
              "newton.verbose": True,
              }

# <markdowncell>
# Now we define the model starting with the exact solution:

# <codecell>
uflSpace = dune.ufl.Space(2, dimRange=1)
x = SpatialCoordinate(uflSpace)
exact = as_vector( [x[0]*x[1] * cos(pi*x[0]*x[1])] )

# next the bilinear form
u = TrialFunction(uflSpace)
v = TestFunction(uflSpace)
a = (inner(grad(u),grad(v))) * dx

# finally the right hand side and the boundary conditions
b = -div(grad(exact[0])) * v[0] * dx
dbc = [dune.ufl.DirichletBC(uflSpace, exact, i+1) for i in range(4)]


# <markdowncell>
# Now we define a grid build up of voronoi cells around $50$ random points

# <codecell>
constructor = cartesianDomain([-0.5,-0.5],[1,1],[1,1])
polyGrid = create.grid("agglomerate", voronoiCells(constructor,50) )

# <markdowncell>
# In general we can construct a `agglomerate` by providing a dictionary with
# the `vertices` and the `polygons`. The `voronoiCells` function creates
# such a dictonary using random seeds to generate voronoi cells which are
# cut off using the provided `cartesianDomain`. The seeds can be
# provided as list of points as second argument:
# ```
# voronoiCells(constructor, towers, fileName=None, load=False):
# ```
# If a `fileName` is provided the seeds will be written to disc and loaded
# from that file is `load=True`. As an example the output of
# `voronoiCells(constructor,5)` is
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

# <codecell>
@gridFunction(polyGrid, name="cells")
def polygons(en,x):
    return polyGrid.hierarchicalGrid.agglomerate(en)
polygons.plot()



# <markdowncell>
# We now define a function to compute the solution and the $L^2,H^1$ error
# given a grid and a space

# <codecell>
def compute(grid, space, schemeName):
    # solve the pde
    scheme = create.scheme(schemeName, [a==b, *dbc], space, solver="cg", parameters=parameters)
    df = space.interpolate([0],name="solution")
    info = scheme.solve(target=df)

    # compute the error
    edf = exact-df
    errors = [ math.sqrt(e) for e in
               integrate(grid, [inner(edf,edf),inner(grad(edf),grad(edf))], order=5) ]

    return df, errors

# <markdowncell>
# Finally we iterate over the requested methods and solve the problems

# <codecell>
for m in methods:
    space = create.space(m[0], polyGrid, order=2, dimRange=1, storage="istl", **m[2])
    dfs,errors = compute(polyGrid, space, m[1])
    print("Size: ",space.size, "L^2: ", errors[0], "H^1: ", errors[1])
    dfs.plot(gridLines=None)


print("END A")
# <markdowncell>
# ## Nonlinear elliptic problem
# We can easily set up a non linear problem
# \begin{align*}
# \end{align*}

# <codecell>
space = create.space("vem", polyGrid, order=2, dimRange=1, storage="istl",
                     conforming=True)
u = TrialFunction(space)
v = TestFunction(space)
x = SpatialCoordinate(space)
exact = as_vector ( [  (x[0] - x[0]*x[0] ) * (x[1] - x[1]*x[1] ) ] )
Dcoeff = lambda u: 1.0 + u[0]**2
a = (Dcoeff(u) * inner(grad(u), grad(v)) ) * dx
b = -div( Dcoeff(exact) * grad(exact[0]) ) * v[0] * dx
dbcs = [dune.ufl.DirichletBC(space, exact, i+1) for i in range(4)]
scheme = create.scheme("vem", [a==b, *dbcs], space, solver="cg", parameters=parameters)
solution = space.interpolate([0], name="solution")
info = scheme.solve(target=solution)
solution.plot(gridLines=None)
print("END B")
# <markdowncell>
# ## Linear Elasticity
# As final example we solve a linear elasticity equation usign a
# conforming VEM space:

# First we setup the domain
# <codecell>
L, W = 1, 0.2

constructor = cartesianDomain([0,0],[L,W],[1,1])
polyGrid = create.grid("agglomerate", voronoiCells(constructor,64) )
@gridFunction(polyGrid, name="cells")
def polygons(en,x):
    return polyGrid.hierarchicalGrid.agglomerate(en)
polygons.plot()

space = create.space("vem", polyGrid, order=2, dimRange=2, storage="istl",
                     conforming=True)

# <markdowncell>

# <codecell>
# some model constants
mu = 1
rho = 1
delta = W/L
gamma = 0.4*delta**2
beta = 1.25
lambda_ = beta
g = gamma

# clamped boundary on the left
x = SpatialCoordinate(space)
dbc = dune.ufl.DirichletBC(space, as_vector([0,0]), x[0]<1e-10)

# Define strain and stress
def epsilon(u):
    return 0.5*(nabla_grad(u) + nabla_grad(u).T)
def sigma(u):
    return lambda_*nabla_div(u)*Identity(2) + 2*mu*epsilon(u)

# Define the variational problem
u = TrialFunction(space)
v = TestFunction(space)
f = dune.ufl.Constant((0, -rho*g))
a = inner(sigma(u), epsilon(v))*dx
b = dot(as_vector([0,-rho*g]),v)*dx

# Compute solution
displacement = space.interpolate([0,0], name="displacement")
scheme = create.scheme("vem", [a==b, dbc], space, solver="cg", parameters=parameters)
info = scheme.solve(target=displacement)

# <markdowncell>
# Show the magnitude of the displacement field

# <codecell>
displacement.plot(gridLines=None)

# <markdowncell>
# We can easily plot the stress

# <codecell>
s = sigma(displacement) - (1./3)*tr(sigma(displacement))*Identity(2)  # deviatoric stress
von_Mises = sqrt(3./2*inner(s, s))
plot(von_Mises, grid=polyGrid, gridLines=None)

# <markdowncell>
# Finally we can plot the actual displaced beam

# <codecell>
from dune.fem.view import geometryGridView
position = space.interpolate( x+displacement, name="position" )
beam = geometryGridView( position )
beam.plot()
