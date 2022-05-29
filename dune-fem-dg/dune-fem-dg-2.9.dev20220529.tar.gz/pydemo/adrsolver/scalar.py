from ufl import *
from dune.ufl import Space
class Transport1D:
    dimRange = 1

    def F_c(t,x,U):
        return as_matrix( [ [U[0], 0] ] )

    boundary = {range(1,5): lambda t,x,u: u}

    def maxWaveSpeed(t,x,U,n):
        return abs(n[0])
    def velocity(t,x,U):
        return as_vector([1,0])
    def physical(t,x,U):
        return 1
    def jump(t,x,U,V):
        return U-V

def LinearAdvectionDiffusion1D(v,eps):
    if v is not None: v = as_vector(v)
    class Model:
        dimRange = 1
        if v is not None:
            def F_c(t,x,U):
                return as_matrix( [[ *(v*U[0]) ]] )
            def maxWaveSpeed(t,x,U,n):
                return abs(dot(v,n))
            def velocity(t,x,U):
                return v*t*10
        if eps is not None:
            def F_v(t,x,U,DU):
                return eps*DU
            # TODO: this method is used in an IMEX method allough the
            # diffusion is explicit - should we change that behaviour?
            # commented out for test of IMEX
            # def maxDiffusion(t,x,U):
            #    return eps
        def physical(t,x,U):
            return conditional( abs( U[0] - 1) > 1e-10, 1, 0 )
        def jump(t,x,U,V):
            return abs(U-V)
    return Model
def LinearAdvectionDiffusion1DMixed(v,eps,bnd):
    class Model(LinearAdvectionDiffusion1D(v,eps)):
        def dirichletValue(t,x,u):
            return bnd(t,x)
        def zeroFlux(t,x,u,n):
            return 0
        def zeroDiffFlux(t,x,u,du,n):
            return 0
        if v is not None and eps is not None:
            boundary = {(1,2): dirichletValue, (3,4): [zeroFlux,zeroDiffFlux] }
        else:
            boundary = {(1,2): dirichletValue, (3,4): zeroFlux }
    return Model
def LinearAdvectionDiffusion1DDirichlet(v,eps,bnd):
    class Model(LinearAdvectionDiffusion1D(v,eps)):
        def dirichletValue(t,x,u):
            return bnd(t,x)
        boundary = { range(1,5): dirichletValue }
    return Model

# burgers problems still need to be adapted to new API
class Burgers1D:
    dimRange = 1
    def F_c(t,x,U):
        return as_matrix( [ [U[0]*U[0]/2, 0] ] )

    boundary = {range(1,5): lambda t,x,u: u}

    def maxWaveSpeed(t,x,U,n):
        return abs(U[0]*n[0])
    def velocity(t,x,U):
        return as_vector( [U[0],0] )
    def physical(t,x,U):
        return 1
    def jump(t,x,U,V):
        return U-V

space = Space(2,1)
x = SpatialCoordinate(space.cell())

def riemanProblem(x,x0,UL,UR):
    return conditional(x<x0,as_vector(UL),as_vector(UR))

def constantTransport():
    return Transport1D, as_vector( [0.1] ),\
           [-1, 0], [1, 0.1], [50, 7], 0.1,\
           "constant", None
def shockTransport():
    return Transport1D, riemanProblem(x[0],-0.5, [1], [0]),\
           [-1, 0], [1, 0.1], [50, 7], 1.0,\
           "shockTransport", None

def sinProblem():
    eps = 0.5
    u0 = lambda t,x: as_vector( [sin(2*pi*x[0])*exp(-t*eps*(2*pi)**2)] )
    return LinearAdvectionDiffusion1DMixed(None,eps,u0), u0(0,x),\
           [-1, 0], [1, 0.1], [50, 7], 0.2,\
           "sin", lambda t: u0(t,x)

def sinTransportProblem():
    eps = 0.5
    v   = [1,0]
    u0 = lambda t,x: as_vector( [sin(2*pi*x[0])*exp(-t*eps*(2*pi)**2)] )
    return LinearAdvectionDiffusion1DMixed(v,eps,u0), u0(0,x),\
           [-1, 0], [1, 0.1], [50, 7], 0.2,\
           "sin", lambda t: u0(t,x)

def pulse(velo=None,eps=None):
    if velo is None:
        center  = as_vector([ 0.5,0.5 ])
        x0 = x[0] - center[0]
        x1 = x[1] - center[1]

        ux = -4.0*x1
        uy =  4.0*x0

        def u0(t,x):
            sig2 = 0.004
            if eps is None:
                sig2PlusDt4 = sig2
            else:
                sig2PlusDt4 = sig2+(4.0*eps*t)
            xq = ( x0*cos(4.0*t) + x1*sin(4.0*t)) + 0.25
            yq = (-x0*sin(4.0*t) + x1*cos(4.0*t))
            return as_vector( [(sig2/ (sig2PlusDt4) ) * exp (-( xq*xq + yq*yq ) / sig2PlusDt4 )] )
        return LinearAdvectionDiffusion1DDirichlet([ux,uy],eps,u0), u0(0,x),\
               [0, 0], [1, 1], [16,16], 1.0,\
               "pulse"+str(eps), lambda t: u0(t,x)
    else:
        return LinearAdvectionDiffusion1DDirichlet(velo,eps,u0), u0(0,x),\
               [0, 0], [1, 1], [16,16], 1.0,\
               "pulse"+str(eps), lambda t: u0(t,x)
def diffusivePulse():
    return pulse(0.001)

def veloDiffusivePulse(velo):
    return pulse(velo,0.001)

def burgersShock():
    Model = Burgers1D
    UL = 1
    UR = 0
    speed = (UL-UR)/2.
    u0 = lambda t,x: riemanProblem(x[0],-0.5+t*speed,[UL],[UR])
    return Model, u0(0,x),\
           [-1, 0], [1, 0.1], [50, 7], 1.,\
           "burgersShock", lambda t: u0(t,x)

def burgersVW():
    Model = Burgers1D
    return Model, riemanProblem(x[0],0,[-1],[1]),\
           [-1, 0], [1, 0.1], [50, 7], 0.7,\
           "burgersShock", None

def burgersStationaryShock():
    Model = Burgers1D
    u0 = lambda t,x: riemanProblem(x[0],0,[1],[-1])
    return Model, u0(0,x),\
           [-1, 0], [1, 0.1], [50, 7], 0.2,\
           "burgersShock", lambda t: u0(t,x)

problems = [ constantTransport, shockTransport, sinProblem,\
             sinTransportProblem, pulse, diffusivePulse,\
             burgersShock, burgersVW, burgersStationaryShock ]
