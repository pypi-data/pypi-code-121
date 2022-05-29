# <codecell>
try:
    get_ipython().magic(u'matplotlib inline # can also use notebook or nbagg')
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
parameters = {"newton.linear.tolerance": 1e-12,
              "newton.linear.preconditioning.method": "ilu",
              "penalty": 40,  # for the bbdg scheme
              "newton.linear.verbose": False,
              }


# <markdowncell>
# As second example we solve a linear elasticity equation usign a
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
L = dot(as_vector([0,-rho*g]),v)*dx

# Compute solution
displacement = space.interpolate([0,0], name="displacement")
scheme = create.scheme("vem", [a==L, dbc], space, solver="cg", parameters=parameters)
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
plot(von_Mises, grid=polyGrid)

# <markdowncell>
# Finally we can plot the actual displaced beam

# <codecell>
from dune.fem.view import geometryGridView
position = space.interpolate( x+displacement, name="position" )
beam = geometryGridView( position )
beam.plot()
