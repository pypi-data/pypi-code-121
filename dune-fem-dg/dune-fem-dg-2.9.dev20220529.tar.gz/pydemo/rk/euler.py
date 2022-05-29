from ufl import *
from dune.ufl import Space

def CompressibleEuler(dim, gamma):
    class Model:
        dimRange = dim+2
        def velo(U):
            return as_vector( [U[i]/U[0] for i in range(1,dim+1)] )
        def rhoeps(U):
            v = Model.velo(U)
            kin = dot(v,v) * 0.5*U[0]
            rE = U[dim+1]
            return rE - kin
        def pressure(U):
            return (gamma-1)*Model.rhoeps(U)
        def toCons(U):
            v = as_vector( [U[i] for i in range(1,dim+1)] )
            rhoEps = U[dim+1]/(gamma-1.)
            kin = dot(v,v) * 0.5*U[0]
            return as_vector( [U[0], *(U[0]*v), rhoEps+kin] )
        def toPrim(U):
            return U[0], Model.velo(U), Model.pressure(U)

        # interface methods
        def F_c(t,x,U):
            assert dim==2
            rho, v, p = Model.toPrim(U)
            rE = U[dim+1]
            # TODO make indpendent of dim
            res = as_matrix([
                    [rho*v[0], rho*v[1]],
                    [rho*v[0]*v[0] + p, rho*v[0]*v[1]],
                    [rho*v[0]*v[1], rho*v[1]*v[1] + p],
                    [(rE+p)*v[0], (rE+p)*v[1]] ] )
            return res
        def maxWaveSpeed(t,x,U,n):
            rho, v, p = Model.toPrim(U)
            return abs(dot(v,n)) + sqrt(gamma*p/rho)
        def velocity(t,x,U):
            return Model.velo(U)
        def physical(t,x,U):
            return conditional( (U[0]>1e-8), conditional( Model.rhoeps(U) > 1e-8 , 1, 0 ), 0 )
        def jump(t,x,U,V):
            pL = Model.pressure(U)
            pR = Model.pressure(V)
            return (pL - pR)/(0.5*(pL + pR))
    return Model

def CompressibleEulerNeuman(dim, gamma, bnd=range(1,5)):
    class Model(CompressibleEuler(dim,gamma)):
        boundary = {bnd: lambda t,x,u,n: Model.F_c(t,x,u)*n}
    return Model
def CompressibleEulerDirichlet(dim, gamma, bnd=range(1,5)):
    class Model(CompressibleEuler(dim,gamma)):
        boundary = {bnd: lambda t,x,u: u}
    return Model
def CompressibleEulerSlip(dim, gamma,bnd=range(1,5)):
    class Model(CompressibleEuler(dim,gamma)):
        def outflowFlux(t,x,u,n):
            _,_, p = CompressibleEuler(dim,gamma).toPrim(u)
            return as_vector([ 0, *(p*n), 0 ])
        boundary = {bnd: outflowFlux}
    return Model

def riemanProblem(Model,x,x0,UL,UR):
    return Model.toCons( conditional(x<x0,as_vector(UL),as_vector(UR)) )

# TODO Add exact solution where available (last argument)
def constant(dim,gamma):
    return CompressibleEulerDirichlet(dim,gamma) ,\
           as_vector( [0.1,0.,0.,0.1] ),\
           [-1, 0], [1, 0.1], [50, 5], 0.1,\
           "constant", None
def sod(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    Model = CompressibleEulerDirichlet(dim,gamma)
    return Model,\
           riemanProblem( Model, x[0], 0.5, [1,0,0,1], [0.125,0,0,0.1]),\
           [0, 0], [1, 0.25], [64, 16], 0.15,\
           "sod", None
def radialSod1(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    Model = CompressibleEulerDirichlet(dim,gamma)
    return Model,\
           riemanProblem( Model, sqrt(dot(x,x)), 0.3,
                          [1,0,0,1], [0.125,0,0,0.1]),\
           [-0.5, -0.5], [0.5, 0.5], [20, 20], 0.25,\
           "radialSod1", None
def radialSod1Large(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    Model = CompressibleEulerDirichlet(dim,gamma)
    return Model,\
           riemanProblem( Model, sqrt(dot(x,x)), 0.3,
                          [1,0,0,1], [0.125,0,0,0.1]),\
           [-1.5, -1.5], [1.5, 1.5], [60, 60], 0.5,\
           "radialSod1Large", None
def radialSod2(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    Model = CompressibleEulerNeuman(dim,gamma)
    return Model,\
           riemanProblem( Model, sqrt(dot(x,x)), 0.3,
                          [0.125,0,0,0.1], [1,0,0,1]),\
           [-0.5, -0.5], [0.5, 0.5], [20, 20], 0.25,\
           "radialSod2", None
def radialSod3(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    Model = CompressibleEulerSlip(dim,gamma)
    return Model,\
           riemanProblem( Model, sqrt(dot(x,x)), 0.3,
                          [1,0,0,1], [0.125,0,0,0.1]),\
           [-0.5, -0.5], [0.5, 0.5], [20, 20], 0.5,\
           "radialSod3", None

def leVeque(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    initial = conditional(abs(x[0]-0.15)<0.05,1.2,1)
    Model = CompressibleEulerDirichlet(dim,gamma)
    return Model,\
           Model.toCons(as_vector( [initial,0,0,initial] )),\
           [0, 0], [1, 0.25], [64, 16], 0.7,\
           "leVeque1D", None

def vortex(dim=2,gamma=1.4):
    S = 13.5    # strength of vortex
    R = 1.5     # radius of vortex
    M = 0.4     # Machnumber

    space = Space(dim,dim+2)
    x     = SpatialCoordinate(space.cell())
    f     = (1. - x[0]*x[0] - x[1]*x[1])/(2.*R*R)
    rho   = pow(1. - S*S*M*M*(gamma - 1.)*exp(2.*f)/(8.*pi*pi), 1./(gamma - 1.))
    u     =      S*x[1]*exp(f)/(2.*pi*R)
    v     = 1. - S*x[0]*exp(f)/(2.*pi*R)
    p     = rho / (gamma*M*M)
    # Model = CompressibleEuler(dim,gamma)
    Model = CompressibleEulerSlip(dim,gamma,bnd=(1,2))
    return Model,\
           Model.toCons( as_vector( [rho,u,v,p] )),\
           [-10, -10], [10, 10], [20, 20], 100,\
           "vortex", None

problems = [sod, radialSod1, radialSod2, radialSod3,\
            radialSod1Large, leVeque, vortex]
