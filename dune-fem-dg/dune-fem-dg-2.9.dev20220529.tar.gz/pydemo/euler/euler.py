from ufl import *
from dune.common import FieldVector
from dune.grid import reader
from dune.ufl import Space, GridFunction
from dune.fem.function import gridFunction
import numpy

def CompressibleEuler(dim, gamma):
    class Model:
        dimRange = dim+2
        def gamma():
            return gamma
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
            rho, v, p = Model.toPrim(U)
            rE = U[dim+1]
            v = numpy.array(v)
            res = numpy.vstack([ rho*v,
                                 rho*numpy.outer(v,v) + p*numpy.eye(dim),
                                 (rE+p)*v ])
            return as_matrix(res)

        def maxWaveSpeed(t,x,U,n):
            rho, v, p = Model.toPrim(U)
            return abs(dot(v,n)) + sqrt(gamma*p/rho)
        def velocity(t,x,U):
            return Model.velo(U)
        def physical(t,x,U):
            return conditional( (U[0]<1e-8), 0, conditional( Model.rhoeps(U) > 1e-8 , 1, 0 ) )
        def jump(t,x,U,V):
            pL = Model.pressure(U)
            pR = Model.pressure(V)
            return (pL - pR)/(0.5*(pL + pR))
        def rotateForth(u, n):
            if dim == 1:
                return [ u[0], n[0]*u[1], u[2] ]
            elif dim == 2:
                return [ u[0], n[0]*u[1] + n[1]*u[2], -n[1]*u[1] + n[0]*u[2], u[3] ]
            elif dim == 3:
                d = sqrt( n[0]*n[0]+n[1]*n[1] )
                if d > 1e-8:
                    d_1 = 1./d
                    return [  u[0],
                              n[0]*u[1] + n[1]*u[2] + n[2]*u[3],
                            - n[1] * d_1 * u[1] + n[0] * d_1 * u[2],
                            - n[0] * n[2] * d_1 * u[1] - n[1] * n[2] * d_1 * u[2] + d * u[3],
                              u[4] ]
                else:
                    return [ u[0], n[2] * u[3], u[2], -n[2] * u[1], u[4] ]

        def rotateBack(u, n):
            if dim == 1:
                return [ u[0], n[0]*u[1], u[2] ]
            elif dim == 2:
                return [ u[0], n[0]*u[1] - n[1]*u[2],  n[1]*u[1] + n[0]*u[2], u[3] ]
            elif dim == 3:
                d = sqrt( n[0]*n[0]+n[1]*n[1] )
                if d > 1e-8:
                    d_1 = 1./d
                    return [  u[0],
                              n[0] * u[1] - n[1]*d_1 * u[2] - n[0]*n[2]*d_1 * u[3],
                              n[1] * u[1] + n[0]*d_1 * u[2] - n[1]*n[2]*d_1 * u[3],
                              n[2] * u[1] + d * u[3],
                              u[4] ]
                else:
                    return [ u[0], -n[2]*u[3], u[2], n[2]*u[1], u[4] ]

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
def CompressibleEulerReflection(dim, gamma,bnd=range(1,5)):
    class Model(CompressibleEuler(dim,gamma)):
        def reflection(t,x,u,n,k):
            uRot = CompressibleEuler(dim,gamma).rotateForth(u, n)
            # flip sign of x-momentum (velocity)
            uRot[ 1 ] = -uRot[ 1 ]
            return as_vector( CompressibleEuler(dim,gamma).rotateBack(uRot, n) )
        boundary = {bnd: reflection}
    return Model

def riemanProblem(Model,x,x0,UL,UR):
    return Model.toCons( conditional(x<x0,as_vector(UL),as_vector(UR)) )

# TODO Add exact solution where available (last argument)
def constant(dim=2,gamma=1.4):
    Model=CompressibleEulerDirichlet(dim,gamma)
    Model.initial=as_vector( [0.1,0.,0.,0.1] )
    Model.domain=[[-1, 0], [1, 0.1], [50, 5]]
    Model.endTime=0.1
    Model.name="constant"
    return Model
def sod(dim=2,gamma=1.4):
    x0 = 0.5
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    Model = CompressibleEulerReflection(dim,gamma)
    Vl, Vr = [1.,0.,0.,1.], [0.125,0,0,0.1]
    Model.initial=riemanProblem( Model, x[0], x0, Vl, Vr)
    Model.domain=[[0, 0], [1, 0.25], [8, 2]]
    Model.endTime=0.15
    def chorin(gv,t):
        gf = gv.function("chorin","chorin.hh", Vl,Vr,gamma,x0,t,name="chorin")
        lgf = gf.localFunction() # this seems to fail?
        @gridFunction(gv,"sod",3)
        def lf(e,x):
            lgf.bind(e)
            y = FieldVector( Model.toCons(lgf(x)) )
            lgf.unbind()
            return y
        # lf.plot()
        return lf
    Model.exact = lambda gv,t: chorin(gv,t)
    Model.name="sod"
    return Model
def radialSod1(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    Model = CompressibleEulerDirichlet(dim,gamma)
    Model.initial=riemanProblem(Model, sqrt(dot(x,x)), 0.3, [1,0,0,1], [0.125,0,0,0.1])
    Model.domain=[[-0.5, -0.5], [0.5, 0.5], [20, 20]]
    Model.endTime=0.25
    Model.name="radialSod1"
    return Model
def radialSod1Large(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    Model = CompressibleEulerDirichlet(dim,gamma)
    Model.initial=riemanProblem( Model, sqrt(dot(x,x)), 0.3, [1,0,0,1], [0.125,0,0,0.1])
    Model.domain=[[-1.5, -1.5], [1.5, 1.5], [60, 60]]
    Model.endTime=0.5
    Model.name="radialSod1Large"
    return Model
def radialSod2(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    Model = CompressibleEulerNeuman(dim,gamma)
    Model.initial=riemanProblem( Model, sqrt(dot(x,x)), 0.3, [0.125,0,0,0.1], [1,0,0,1])
    Model.domain=[[-0.5, -0.5], [0.5, 0.5], [20, 20]]
    Model.endTime=0.25
    Model.name="radialSod2"
    return Model
def radialSod3(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    Model = CompressibleEulerSlip(dim,gamma)
    Model.initial=riemanProblem( Model, sqrt(dot(x,x)), 0.3, [1,0,0,1], [0.125,0,0,0.1])
    Model.domain=[[-0.5, -0.5], [0.5, 0.5], [20, 20]]
    Model.endTime=0.5
    Model.name="radialSod3"
    return Model
def leVeque(dim=2,gamma=1.4):
    space = Space(dim,dim+2)
    x = SpatialCoordinate(space.cell())
    initial = conditional(abs(x[0]-0.15)<0.05,1.2,1)
    Model = CompressibleEulerDirichlet(dim,gamma)
    Model.initial=Model.toCons(as_vector( [initial,0,0,initial] ))
    Model.domain=[[0, 0], [1, 0.25], [64, 16]]
    Model.endTime=0.7
    Model.name="leVeque1D"
    return Model

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
    Model.initial=Model.toCons( as_vector( [rho,u,v,p] ))
    Model.domain=[[-10, -10], [10, 10], [20, 20]]
    Model.endTime=100
    Model.name="vortex"
    return Model

problems = [sod, radialSod1, radialSod2, radialSod3,\
            radialSod1Large, leVeque, vortex]
