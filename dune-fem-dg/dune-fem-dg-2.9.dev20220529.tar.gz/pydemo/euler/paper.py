import math, sys
from ufl import *
from dune.generator import path
from dune.grid import structuredGrid
from dune.fem.space import dgonb, finiteVolume
from dune.femdg import femDGOperator
from dune.femdg.rk import femdgStepper

# Basic model for hyperbolic conservation law
class Model:
    gamma = 1.4
    # helper function
    def toPrim(U):
        v = as_vector( [U[i]/U[0] for i in range(1,3)] )
        kin = dot(v,v) * U[0] / 2
        pressure = (Model.gamma-1)*(U[3]-kin)
        return U[0], v, pressure

    # interface methods for model
    def F_c(t,x,U):
        rho, v, p = Model.toPrim(U)
        return as_matrix( [
                  [rho*v[0], rho*v[1]],
                  [rho*v[0]*v[0] + p, rho*v[0]*v[1]],
                  [rho*v[0]*v[1], rho*v[1]*v[1] + p],
                  [(U[3]+p)*v[0], (U[3]+p)*v[1]] ] )
    # simple 'outflow' boundary conditions on all boundaries
    boundary = {range(1,5): lambda t,x,U: U}

    # interface method needed for LLF and time step control
    def maxWaveSpeed(t,x,U,n):
        rho, v, p = Model.toPrim(U)
        return abs(dot(v,n)) + sqrt(Model.gamma*p/rho)

########################################################################

print("\n###############\n Start Part 1\n",flush=True)

# Part 1: basic set up and time loop - no limiter and fixed time step
#         using constant initial data
gridView = structuredGrid([-1,-1],[1,1],[40,40])
space = dgonb( gridView, order=3, dimRange=4)
operator = femDGOperator(Model, space, limiter=None)
stepper  = femdgStepper(order=3, operator=operator)
u_h = space.interpolate([1.4,0,0,1], name='u_h')
t  = 0
# don't show vtk in paper
vtk = gridView.sequencedVTK("paperA", pointdata=[u_h])
while t < 0.1:
    operator.setTime(t)
    t += stepper(u_h, dt=0.001)
vtk()

##############################################################
# Part 2: add limiter and methods for troubled cell indicator
print("\n###############\n Start Part 2\n",flush=True)
def velocity(t,x,U):
    _, v ,_ = Model.toPrim(U)
    return v
def physical(t,x,U):
    rho, _, p = Model.toPrim(U)
    return conditional( rho>1e-8, conditional( p>1e-8 , 1, 0 ), 0 )
def jump(t,x,U,V):
    _,_, pL = Model.toPrim(U)
    _,_, pR = Model.toPrim(V)
    return (pL - pR)/(0.5*(pL + pR))
# don't show the following lines just explain that the above method is added to the Model
Model.velocity = velocity
Model.physical = physical
Model.jump     = jump

def femdgFlux():
    return femDGOperator(Model, space, limiter="MinMod")
def headerFlux():
    fluxHeader = path(__file__)+"llf.hh"
    return femDGOperator(Model, space, advectionFlux=fluxHeader, limiter="MinMod")
def classFlux():
    def flux(model,clsName,includes): # possibly also want to pass in parameters
        from dune.generator.importclass import load
        return load(clsName,[path(__file__)+"llf.hh"]+includes,model)
    return femDGOperator(Model, space, advectionFlux=flux, limiter="MinMod")
versions = [classFlux] # [femdgFlux,headerFlux,classFlux]
for op in versions:
    print("####", op.__name__,flush=True)
    operator = op()
    stepper  = femdgStepper(order=3, operator=operator)
    x = SpatialCoordinate(space)
    u_h.interpolate( conditional(dot(x,x)<0.1,as_vector([1,0,0,2.5]),
                                              as_vector([0.125,0,0,0.25])) )
    operator.applyLimiter(u_h)
    t  = 0
    vtk = gridView.sequencedVTK("paperB"+op.__name__, pointdata=[u_h])
    while t < 0.004:
        vtk()
        operator.setTime(t)
        t += stepper(u_h)
        print(t)
    vtk()

# Part 3: FV on polygonal grid
print("\n###############\n Start Part 3\n",flush=True)
from dune.generator import algorithm
from dune.polygongrid import voronoiDomain, polygonGrid
from dune.grid import reader

import numpy

x0 = [-1,-1]
x1 = [ 1, 1]
N  = [40,40]
#boundingBox = numpy.array([ x0, x1 ])
#vb = voronoiDomain(N[0]*N[1], boundingBox, seed=1234)

domain = (reader.dgf, "triangle.dgf")
gridView = polygonGrid( domain, dualGrid=True )
space = dgonb( gridView, order=1, dimRange=4 )
u_h   = space.interpolate( conditional(dot(x,x)<0.1,as_vector([1,0,0,2.5]),
                                                    as_vector([0.125,0,0,0.25])),
                                                    name="uh")
fvspc = finiteVolume( gridView, dimRange=4)
fvU = fvspc.interpolate( u_h, name = "fvU" )

operator = femDGOperator(Model, space, limiter="MinMod")
stepper  = femdgStepper(order=1, operator=operator, cfl=0.4)
operator.applyLimiter(u_h)
count = 0
gridView.writeVTK("paperC", celldata=[fvU], number=count)
t  = 0
while t < 0.4:
    assert not math.isnan( u_h.scalarProductDofs( u_h ) )
    operator.setTime(t)
    t += stepper(u_h)
    print(t)
    fvU.interpolate( u_h )
    count += 1
    gridView.writeVTK("paperC", celldata=[fvU], number=count)
